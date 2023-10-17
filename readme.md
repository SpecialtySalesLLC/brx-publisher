# Publish messages to Brx IoT Core
publisher.py will publish messages randomly generated every 10 seconds to simulate a Brx device. The published messages will be stored in a database table for further processing.

# Setup new device Brx IoT Core
## Create new Thing and certificates
- Log into AWS console and make sure to access AWS IoT dashboard in Ohio region
- Select Manage menu option, then click Things in the sub menu. Choose create things
- Choose Create a single thing
- Specify Thing properties and choose No shadow then click Next
- Choose Auto-generate a new certificate then Click Next
- In the policies page, choose Brx-Iot-Policy then click on Create thing
- Make sure to Download:
  - Device Certificate
  - Public key file
  - Private key file
  - Amazon Root CA1
- After downloading the above certs and key files, click on Done. 

## Copy files to new device
- First rename the files in your local system before uploading them to the new device
  - Rename device certificate to certificate.pem
  - Rename private key to privateKey.pem
  - Rename Amazon root CA1 to AmazonRootCA1.pem
- Download the publisher.py from [Github](https://github.com/SpecialtySalesLLC/brx-publisher/blob/main/publisher.py)
- Edit publisher.py 
- Set the following variables to their appropriate values based on the new created device:
  - thing_name
  - device_id
- By default frequency to publish messages is set to 10 seconds, change it to whatever number of seconds
- Upload all files, certificates and publisher.py to the new device, they have to be located within same folder

## Publish messages
- From the new device, enter bush commands
- If AWS IoT Device SDK for Python v2 is not install, run the following command in the terminal:
`pip3 install awsiotsdk`
- Change directory to publisher folder then run the following command:
`python3 publisher.py`

# Check database for published messages
- From AWS console, navigate to DynamoDB in Ohio region
- From the Tables menu select Explore Items
- Select brx_dev_messages table

