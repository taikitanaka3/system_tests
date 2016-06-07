# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import functools
import os
import sys

# this is needed to allow import of test_communication messages
sys.path.insert(0, os.getcwd())
# this is needed to allow rclpy to be imported from the build folder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.getcwd())), 'rclpy'))


def listener_cb(msg, received_messages, expected_msgs):
    known_msg = False
    for exp in expected_msgs:
        if msg.__repr__() == exp.__repr__():
            print('received message #{} of {}'.format(
                expected_msgs.index(exp) + 1, len(expected_msgs)))
            known_msg = True
            already_received = False
            for rmsg in received_messages:
                if rmsg.__repr__() == msg.__repr__():
                    already_received = True
                    break

            if not already_received:
                received_messages.append(msg)
            break
    if known_msg is False:
        raise RuntimeError('received unexpected message %r' % msg)


def listener(message_name, rmw_implementation, number_of_cycles):
    import rclpy
    from rclpy.qos import qos_profile_default
    from rclpy.impl.rmw_implementation_tools import select_rmw_implementation

    select_rmw_implementation(rmw_implementation)

    rclpy.init([])

    # TODO(wjwwood) move this import back to the module level when
    # it is possible to import the messages before rclpy.init().
    from message_fixtures import get_test_msg

    node = rclpy.create_node('listener')

    received_messages = []
    expected_msgs = get_test_msg(message_name)

    chatter_callback = functools.partial(
        listener_cb, received_messages=received_messages, expected_msgs=expected_msgs)

    if 'builtins' == message_name:
        from test_communication.msg import Builtins
        assert Builtins.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            Builtins, 'test_message_' + message_name, chatter_callback,
            qos_profile_default)
    elif 'empty' == message_name:
        from test_communication.msg import Empty
        assert Empty.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            Empty, 'test_message_' + message_name, chatter_callback, qos_profile_default)
    elif 'primitives' == message_name:
        from test_communication.msg import Primitives
        assert Primitives.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            Primitives, 'test_message_' + message_name, chatter_callback, qos_profile_default)
    elif 'nested' == message_name:
        from test_communication.msg import Nested
        assert Nested.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            Nested, 'test_message_' + message_name, chatter_callback, qos_profile_default)
    elif 'fieldswithsametype' == message_name:
        from test_communication.msg import FieldsWithSameType
        assert FieldsWithSameType.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            FieldsWithSameType, 'test_message_' + message_name, chatter_callback,
            qos_profile_default)
    elif 'staticarraynested' == message_name:
        from test_communication.msg import StaticArrayNested
        assert StaticArrayNested.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            StaticArrayNested, 'test_message_' + message_name, chatter_callback,
            qos_profile_default)
    elif 'staticarrayprimitives' == message_name:
        from test_communication.msg import StaticArrayPrimitives
        assert StaticArrayPrimitives.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            StaticArrayPrimitives, 'test_message_' + message_name, chatter_callback,
            qos_profile_default)
    elif 'dynamicarrayprimitives' == message_name:
        from test_communication.msg import DynamicArrayPrimitives
        assert DynamicArrayPrimitives.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            DynamicArrayPrimitives, 'test_message_' + message_name, chatter_callback,
            qos_profile_default)
    elif 'dynamicarraynested' == message_name:
        from test_communication.msg import DynamicArrayNested
        assert DynamicArrayNested.__class__._TYPE_SUPPORT is not None
        node.create_subscription(
            DynamicArrayNested, 'test_message_' + message_name, chatter_callback,
            qos_profile_default)

    spin_count = 1
    print('subscriber: beginning loop')
    while (rclpy.ok() and spin_count < number_of_cycles and
           len(received_messages) != len(expected_msgs)):
        rclpy.spin_once(node)
        spin_count += 1
    rclpy.shutdown()

    assert len(received_messages) == len(expected_msgs),\
        'Should have received {} {} messages from talker'.format(len(expected_msgs), message_name)

if __name__ == '__main__':
    from rclpy.impl.rmw_implementation_tools import get_rmw_implementations
    rmw_implementations = get_rmw_implementations()
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('message_name', default='primitives',
                        help='name of the ROS message')
    parser.add_argument('-r', '--rmw_implementation', default=rmw_implementations[0],
                        choices=rmw_implementations,
                        help='rmw_implementation identifier')
    parser.add_argument('-n', '--number_of_cycles', type=int, default=10,
                        help='number of sending attempts')
    args = parser.parse_args()
    try:
        listener(
            message_name=args.message_name,
            rmw_implementation=args.rmw_implementation,
            number_of_cycles=args.number_of_cycles)
    except KeyboardInterrupt:
        print('subscriber stopped cleanly')
    except BaseException:
        print('exception in subscriber:', file=sys.stderr)
        raise
