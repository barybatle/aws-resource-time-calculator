# CloudFormation Stack Events Analyzer

## Overview

This script allows you to analyze CloudFormation stack events to determine the creation or deletion times of resources within a stack.

## Prerequisites

- Python 3.x
- Boto3 library (`pip install boto3`)
- AWS credentials set up in the `.aws` directory (either `~/.aws/credentials` or using environment variables)

## Usage
1. Navigate to the script directory.

    ```bash
    cd your-repository
    ```

2. Install the required dependencies.

    ```bash
    pip install boto3
    ```

3. Ensure AWS credentials are set up in the `.aws` directory.

    - Either configure the `~/.aws/credentials` file with your AWS Access Key ID and Secret Access Key:

        ```
        [default]
        aws_access_key_id = YOUR_ACCESS_KEY_ID
        aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
        ```

    - Or set the necessary environment variables (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).

4. Run the script with the following command:

    ```bash
    python resourceTimeCalculator.py -s STACK_NAME -o OPERATION -r REGION
    ```

    - `STACK_NAME`: Name of the CloudFormation stack.
    - `OPERATION`: Either 'create' or 'delete' for calculating creation and deletion times (default is 'create').
    - `REGION`: AWS region (default is 'eu-west-1').

5. Review the output, which will display resources with the longest creation or deletion times. 
- Alternatively you can add '> file.txt' to command so it saves output to a file.

## Example

```bash
python resourceTimeCalculator.py -s MyStack -o create -r us-east-1
python resourceTimeCalculator.py -s MyStack -o create -r us-east-1 > output.txt
```

## Credits

v1.0.0 created by barybatle@gmail.com
