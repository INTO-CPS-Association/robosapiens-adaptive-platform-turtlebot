#include "scan_modifier.hpp"
#include <sstream>
#include <cmath>
#include <rclcpp/rclcpp.hpp>

namespace scan
{

  using namespace std::placeholders;
  using ranges_t = ScanModifierNode::ranges_t;

  std::string pair_vec_to_str(const std::vector<std::pair<uint16_t, uint16_t>> &vec)
  {
    std::ostringstream oss;
    oss << "[";
    for (size_t i = 0; i < vec.size(); ++i)
    {
      oss << "(" << vec[i].first << ", " << vec[i].second << ")";
      if (i != vec.size() - 1)
      {
        oss << ", ";
      }
    }
    oss << "]";
    return oss.str();
  }

  // Copied from: /nav2_util/node_utils.hpp
  template <typename NodeT>
  void declare_parameter_if_not_declared(
      NodeT node, const std::string &param_name, const rclcpp::ParameterType &param_type,
      const rcl_interfaces::msg::ParameterDescriptor &parameter_descriptor = rcl_interfaces::msg::ParameterDescriptor())
  {
    if (!node->has_parameter(param_name))
    {
      node->declare_parameter(param_name, param_type, parameter_descriptor);
    }
  }

  void print_laser(const sensor_msgs::msg::LaserScan &msg, const rclcpp::Logger &logger)
  {
    RCLCPP_DEBUG(logger,
                 "Message: angle_min: %f, angle_max: %f, angle_increment: %f, time_increment: %f, scan_time: %f, "
                 "range_min: %f, range_max: %f",
                 msg.angle_min, msg.angle_max, msg.angle_increment, msg.time_increment, msg.scan_time, msg.range_min,
                 msg.range_max);
    std::stringstream ss;
    for (const auto &v : msg.ranges)
    {
      ss << v;
      ss << ", ";
    }
    auto result = ss.str();
    // RCLCPP_DEBUG(logger, "Ranges: %s", result.c_str());
  }

  ScanModifierNode::ScanModifierNode() : Node("scan_modifier")
  {
    scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
        "/scan", rclcpp::SensorDataQoS(), std::bind(&ScanModifierNode::scan_sub_callback, this, _1));
    publisher_ = create_publisher<sensor_msgs::msg::LaserScan>("/scan_safe", rclcpp::SensorDataQoS());
    config_sub_ = create_subscription<std_msgs::msg::UInt16MultiArray>(
        "/scan_config", rclcpp::ServicesQoS(), std::bind(&ScanModifierNode::config_sub_callback, this, _1));

    constexpr auto param_name = "scan_ranges_size";
    this->declare_parameter(param_name, rclcpp::ParameterType::PARAMETER_INTEGER);
    auto lidar_filt_upper = this->get_parameter(param_name).as_int();
    lidar_filters_ = {{0, lidar_filt_upper}};

    RCLCPP_INFO(get_logger(), "Scan modifier node started!");
    RCLCPP_INFO(get_logger(), "Scan size: %ld", lidar_filt_upper);
  }

  void ScanModifierNode::config_sub_callback(const std_msgs::msg::UInt16MultiArray::SharedPtr config)
  {
    if (config->data.size() % 2 != 2)
    {
      lidar_filters_.clear();
      for (size_t i = 0; i < config->data.size(); i += 2)
      {
        lidar_filters_.emplace_back(std::make_pair(config->data[i], config->data[i + 1]));
      }

      RCLCPP_INFO(get_logger(), "Setting non-occluded areas to: %s", pair_vec_to_str(lidar_filters_).c_str());
    }
    else
    {
      RCLCPP_WARN(get_logger(), "Received incorrectly formatted config data. Expected an even number of ints.");
    }
  }

  void ScanModifierNode::scan_sub_callback(const sensor_msgs::msg::LaserScan::SharedPtr laser_msg)
  {
    constexpr auto between_any = [](const auto &val, const auto &vec)
    {
      return std::any_of(vec.begin(), vec.end(), [&val](const auto &pair)
                         { return val >= pair.first && val <= pair.second; });
    };

    const auto &logger = get_logger();
    RCLCPP_DEBUG(get_logger(), "Data size: %ld. Scan config: %s",
                 laser_msg->ranges.size(), pair_vec_to_str(lidar_filters_).c_str());

    for (size_t i = 0; i < laser_msg->ranges.size(); i++)
    {
      if (!between_any(i, lidar_filters_))
      {
        laser_msg->ranges[i] = -std::numeric_limits<float>::infinity();
      }
    }

    publisher_->publish(*laser_msg);
  }
} // namespace scan

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<scan::ScanModifierNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}