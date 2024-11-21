# Greengrass Hello World PubSub Component

This is a simplified "Hello World" version of the sample provided in the official repository for [AWS IoT Greengrass PubSub SDK for Python](https://github.com/awslabs/aws-greengrass-labs-iot-pubsub-sdk-for-python/tree/main/samples). This simple component demonstrates basic publish/subscribe functionality using both MQTT and IPC protocols in AWS IoT Greengrass V2.

For a more complete framework with custom routes, default egress/ingress topics, and more debugging information, please reference original source repository above. Sections of the readme from that github have been copied in here for convenience and so that this is a standalone guide for a simple component


### Prerequisites
* An AWS Account, see [How to Create a new AWS account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) if needed.
* A registered [AWS Greengrass V2 core device](https://docs.aws.amazon.com/greengrass/v2/developerguide/setting-up.html)
* Knowledge of [AWS Greengrass Components](https://docs.aws.amazon.com/greengrass/v2/developerguide/create-components.html) and the [AWS Greengrass Developer Guide](https://docs.aws.amazon.com/greengrass/v2/developerguide).
* The [AWS Greengrass Development Kit](https://docs.aws.amazon.com/greengrass/v2/developerguide/greengrass-development-kit-cli.html) installed on the development machine. 
    *  Ensure your development machine has the AWS GDK installed by following this guide to [Install or Update the AWS IoT Greengrass Development Kit Command-Line Interface](https://docs.aws.amazon.com/greengrass/v2/developerguide/install-greengrass-development-kit-cli.html).

### Clone and Copy the Component Template

```
# Clone this GIT Repository
MY_COMPONENT_NAME=GreenGrassV2HelloWorld
git clone https://github.com/myles-i/GreenGrassV2HelloWorld.git ${MY_COMPONENT_NAME}

cd ${MY_COMPONENT_NAME}/src
```

**Note:** Its recommended to open the new component directory in your preferred IDE or text editor now to help with making the proceeding changes and updates.


### Update the GDK Configuration
The SDK component template is built and published using the AWS Greengrass Development Kit, with behaviors set by the **src/gdk-config.json** config file.

In the AWS Greengrass component directory:
* Update the **author** and **region** fields accordingly. (Ensure region supports AWS Greengrass)
* If you changed the component name (i.e: MY_COMPONENT_NAME) above, then update **com.example.greengrass-pubsub-component** here as well. 

**Notes:**
* The GDK will create a unique Amazon S3 bucket to host the component artifacts with the name based on the bucket value, your account ID and the selected region. 
* Each component will be given a unique folder and so you can use this S3 bucket globally for all AWS Greengrass components.
* Your AWS Identity and Access Management (IAM) permissions must allow Amazon S3 bucket creation and publishing AWS IoT Greengrass components.

## Functionality (defined in src/main.py)

This component:
1. Initializes the AWS Greengrass PubSub SDK client
2. Activates both MQTT and IPC PubSub
3. Subscribes to a topic
4. Publishes a "Hello World" message every 5 seconds
5. Logs any received messages

The component is configued on the greengrass core via the recipe.json file.

### Build and Publish the Component to AWS IoT Core
If not already completed, ensure your development machine has the AWS GDK installed by following this guide to [Install or Update the AWS IoT Greengrass Development Kit Command-Line Interface](https://docs.aws.amazon.com/greengrass/v2/developerguide/install-greengrass-development-kit-cli.html).

```
# (If not already done, CD into the component src directory
cd $MY_COMPONENT_NAME/src

# Build the component:
gdk component build

# Publish the component to AWS IoT Core:
gdk component publish

```

The AWS Greengrass component will now be published to the AWS IoT Core. You can verify in the [AWS IoT Console](https://console.aws.amazon.com/iot/) by selecting your **region** then, selecting **Greengrass** and the **Components** menu as shown below:


### Deploy the Component to an AWS Greengrass Core Device

**Note:** The AWS Greengrass Core device will need permissions to access the S3 bucket with the deployment artifact listed in  src/gdk-config.json as described above. See [Authorize core devices to interact with AWS services](https://docs.aws.amazon.com/greengrass/v2/developerguide/device-service-role.html) in the AWS Greengrass Developer guide for details. 

The final step is to deploy the component to a registered AWS Greengrass Core device:
* In the [AWS IoT Console](https://console.aws.amazon.com/iot/), select **Greengrass** and then the **Core devices** menu item and click on the Greengrass core you will deploy the component on.

* Select the **Deployments** tab and click on the managed deployment to add this component too
  * If your Greengrass Core device doesn’t have an existing deployment, you will need to create one by going to the **Deployments** menu item, clicking **Create**, select the Core device and then following the below instructions from there.
* Click **Revise**, **Revise Deployment** then **Next** and select the name of the component you published in the **My components** section.
* Click **Next** leaving all fields default until the final page then click **Deploy**

## Validate the Component
The pub/sub handling in the component can verified in the IoT Console in the "MQTT test client"

Once the template component and SDK are installed and operational on an AWS Greengrass core device, it will periodically the below message to the topic "GGHelloWorld/outbox"
```
{
  "sdk_version": "0.1.4",
  "message_id": "20240930175859601678",
  "status": 200,
  "route": "default_message_handler",
  "message": {
    "user_msg": "Hello World, from GreenGrassCore V2"
  }
}
```

The component will also process and print messages on the GreenGrass core device for messages published to topic "GGHelloWorld/inbox". You can try this out in the  "MQTT test client". For example, you can try publishing this message to the "GGHelloWorld/inbox" topic:
```
{
  "sdk_version": "0.1.4",
  "message_id": "20240930180857201116",
  "status": 200,
  "route": "default_message_handler",
  "message": {
    "user_msg": "Hello World, from IoT CONSOLE"
  }
}
```

### Monitoring Greengrass and Component Logs:

Greengrass logs (on the Greengrass Core device) are located in the /greengrass/v2/logs directory.

To fault find or just to view component application logs, on the Greengrass Core device:

```
# To display the status of the deployment and any recent errors on the Greengrass core
tail -f /greengrass/v2/logs/greengrass.log

# The application log for the Greengrass component and will show errors and messages being published and received.
tail -f /greengrass/v2/logs/MY_COMPONENT_NAME.log
```