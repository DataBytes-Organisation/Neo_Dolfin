# DolFin Infrastructure as Code

The infra folder contains a Terraform project that creates the following infrastructure in Google Cloud Platform (GCP)

- A VPC with subnet
- Cloud SQL instance using MySql
- VM instance with Flask installed

Further work will add modules for provisioning AI infrastructure

**This is a work in progress and not guaranteed to be ready for the app to be deployed on**

## Getting Started

### Install the Google Cloud CLI

https://cloud.google.com/sdk/docs/install

### Install Terraform

https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

### Generate a Service Key

**IMPORTANT - The service key contains sensitive information and MUST NOT be checked into source control**

- Navigate to Service Accounts in IAM and Admin.
- Select "Create Service Account"
- Give it a name and description
- Assign the following roles: Editor, Compute Network Admin
- Download the key as json and save it to a secure local folder, outside of the project


### Create the State Bucket

The state bucket is used to store Terraform state remotely, allowing multiple to work on the Terraform code without breaking each others configurations.

In the GCP console do the following:

- Navigate to Cloud Storage
- Click Create and enter the following details and click Create
    - Bucket name: ```dolfin```
    - Location type: ```Region```, select ```australia-southeast1```
    - Storage class: ```Standard```
    - Access: ```Enforce public access prevention on this bucket```

### Configure Local Variables

In the file neo_dolfin/infra/variables.tf add the project_id for the DolFin GCP project

```
variable "gcp_project_id" {
    default = "GCP_PROJECT_NAME"
}
```

### Initialise the project

Navigate to the infra folder in your terminal and run the following steps:

#### Enable the required GCP API's

- Make the file executable if you are on a Mac
```chmod a+x ./bootstrap.sh```

- Run the bootstrap file
```./bootstrap.sh```

#### Initialise and Deploy the Project

```terraform initialise```

```terraform plan -var credentials_file=./path_to_your_creds.json```

```terraform deploy -auto-approve -var credentials_file=./path_to_your_creds.json```

