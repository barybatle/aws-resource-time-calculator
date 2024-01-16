import argparse
import boto3
from datetime import datetime

CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
CREATE_COMPLETE = "CREATE_COMPLETE"
DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
DELETE_COMPLETE = "DELETE_COMPLETE"


def get_all_events(stack_name, region):
    """
    Get all CloudFormation stack events.

    Args:
        stack_name (str): Name of the CloudFormation stack.
        region (str): AWS region.

    Returns:
        list: List of CloudFormation stack events.
    """
    cloudformation_client = boto3.client('cloudformation', region_name=region)

    all_events = []

    next_token = None
    while True:
        if next_token:
            response = cloudformation_client.describe_stack_events(
                StackName=stack_name,
                NextToken=next_token
            )
        else:
            response = cloudformation_client.describe_stack_events(StackName=stack_name)

        events = response.get('StackEvents', [])
        all_events.extend(events)

        next_token = response.get('NextToken')

        if not next_token:
            break

    return all_events


def calculate_time_difference(start_time, end_time):
    """
    Calculate the time difference in seconds between two datetime objects.

    Args:
        start_time (datetime): Start time.
        end_time (datetime): End time.

    Returns:
        float: Time difference in seconds.
    """
    return (end_time - start_time).total_seconds()


def find_resources_with_longest_time(events, operation):
    """
    Find resources with the longest creation or deletion times.

    Args:
        events (list): List of CloudFormation stack events.
        operation (str): Either 'create' or 'delete'.

    Returns:
        list: List of resource times sorted by duration in descending order.
    """
    resource_times = {}

    for event in events:
        resource_id = event.get("LogicalResourceId")

        if operation == "create":
            status_in_progress = CREATE_IN_PROGRESS
            status_complete = CREATE_COMPLETE
        elif operation == "delete":
            status_in_progress = DELETE_IN_PROGRESS
            status_complete = DELETE_COMPLETE
        else:
            raise ValueError("Invalid operation. Use 'create' or 'delete'.")

        if event.get("ResourceStatus") == status_in_progress:
            if resource_id in resource_times or event.get("Timestamp") < resource_times.get(resource_id, {}).get("start_time"):
                resource_times[resource_id]["start_time"] = event.get("Timestamp")
            elif resource_id not in resource_times:
                resource_times[resource_id] = {
                    "start_time": event.get("Timestamp"),
                    "end_time": None
                }

        elif event.get("ResourceStatus") == status_complete:
            if resource_id in resource_times:
                resource_times[resource_id]["end_time"] = event.get("Timestamp")
            elif resource_id not in resource_times:
                resource_times[resource_id] = {
                    "start_time": None,
                    "end_time": event.get("Timestamp")
                }

    for resource_id, times in resource_times.items():
        times["duration"] = calculate_time_difference(times.get("start_time", datetime.min), times.get("end_time", datetime.min))

    sorted_resources = sorted(resource_times.items(), key=lambda x: x[1]["duration"], reverse=True)

    return sorted_resources


def analyze_events(events, operation):
    """
    Analyze CloudFormation stack events and print resources with the longest creation or deletion times.

    Args:
        events (list): List of CloudFormation stack events.
        operation (str): Either 'create' or 'delete'.
    """
    if operation not in ['create', 'delete']:
        print("Invalid operation. Use 'create' or 'delete'.")
    else:
        sorted_resources = find_resources_with_longest_time(events, operation)

        print(f"Resources with longest {operation} times:")
        for resource_id, times in sorted_resources:
            print(f"{resource_id}: {times['duration']} seconds")


def calculate_times(stack_name, region, operation):
    """
    Calculate and analyze creation or deletion times for a CloudFormation stack.

    Args:
        stack_name (str): Name of the CloudFormation stack.
        region (str): AWS region.
        operation (str): Either 'create' or 'delete'.
    """
    events = get_all_events(stack_name, region)
    analyze_events(events, operation)


def main():
    parser = argparse.ArgumentParser(description='Describe CloudFormation stack events.')
    parser.add_argument('-s', '--stack-name', required=True, help='Name of the CloudFormation stack')
    parser.add_argument('-o', '--operation', required=False, default='create', choices=['create', 'delete'],
                        help='create/delete for calculating creation and deletion times')
    parser.add_argument('-r', '--region', required=False, default='eu-west-1', help='AWS region')

    args = parser.parse_args()

    calculate_times(args.stack_name, args.region, args.operation)


if __name__ == "__main__":
    main()
