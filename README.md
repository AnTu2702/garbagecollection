# garbagecollection

THIS IS SOME QUICK AND DIRTY CODE ONLY FOR PERSONAL EVALUATION

An AWS CloudWatch Event gets triggered every evening to call an AWS lambda which checks the garbage collection at my address for the next day.
If any garbage collection takes place the next day at my address, an SNS notification is send (which will inform my family via email/push)

Files:

- dependencies.zip
  All ec2 precompiled python modules for AWS lambda usage needed for abfall.py. (will only work with EC2 Amazon Linux, do not use locally)

- abfall.py 
  Contains the main lambda entry point.

Usage:

To use this code as lambda:

1. unzip dependencies.zip
2. zip -r abfall.zip * --exclude dependencies.zip
3. upload abfall.zip to your AWS Lambda
4. Trigger Lambda by AWS CloudWatch Event
