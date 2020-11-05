# OCS-migrate

## Overview

`ocs-migrate` automates migration of PersistentVolumeClaims (PVCs) and PersistentVolumes (PVs) from any storage provider to OCS

### Prerequisite steps

* The application on the source side needs to be quiesced before attempting migration
* PVs to be migrated need to be attached with pods, unattached PVs will not be migrated
* Storage Class Selections must be made - [Instructions](./docs/sc-selection.md)

## Usage

### 1. Clone this git repo

```bash
git clone https://github.com/mulbc/ocs-migrate && cd ocs-migrate
```

### 2. Automation prerequisites

#### Virtualenv

* Installing Virtualenv

```bash
python3 -m pip install --user virtualenv
python3 -m venv env
```

* Activate Virtualenv and install requirements

```bash
source env/bin/activate
pip install -r requirements.txt
```

* Install selinux dependency if selinux is enabled

```bash
pip install selinux
```

* To update any requirements

```bash
pip freeze &> requirements.txt
```

#### Without Virtualenv

```bash
pip3 install ansible==2.9.7 --user      # ansible 2.9
pip3 install kubernetes==11.0.0 --user  # kubernetes module for ansible
pip3 install openshift==0.11.2 --user   # openshift module for ansible
pip3 install PyYAML==5.1.1 --user       # pyyaml module for python
pip3 install jmespath==0.10.0 --user    # for json querying from ansible
pip3 install urllib3==1.24.2 --user     # stage 1 requirement

sudo dnf install jq                     # jq-1.6 for json processing
sudo dnf install bind-utils
sudo dnf install dnsutils
sudo dnf install python3-libselinux
```

### 4. Set list of namespaces to migrate PVC data for

1. Copy sample config file as starting point: `cp 1_pvc_data_gen/vars/pvc-data-gen.yml.example 1_pvc_data_gen/vars/pvc-data-gen.yml`

1. Edit `1_pvc_data_gen/vars/pvc-data-gen.yml`, adding the list of namespaces for which PV/PVC data should be migrated

```yaml
namespaces_to_migrate:
 - rocket-chat
 - nginx-pv
```

### 5. Familiarize with PVC migration automation

The `pvc-migrate` tooling is designed to work in 3 stages :

#### Stage 1 - Detect source cluster info (PVCs, Pods, Nodes) ([Stage 1 README](1_pvc_data_gen))

`1_pvc_data_gen`

This preliminary stage collects information about PVCs, PVs and Pods that are to be migrated. It creates a JSON report of collected data which will be consumed by subsequent stages.

**Note**: Changes of source PVs and PVCs after completion of Stage 1 will not be considered by next stages. You can re-run stage 1 to refresh data as needed before running Stages 2 and 3.

#### Stage 2 - Migrate PVC definitions to destination cluster ([Stage 2 README](2_pvc_destination_gen))

`2_pvc_destination_gen`

This stage creates the target PVs and PVCs on OCS where the data will be migrated to. No data will be moved in this stage yet.

**Note**: This stage __requires__ users to provide Storage Class selections. Please see notes on [Storage Class Selection](./docs/sc-selection.md)

#### Stage 3 - RSync PVC data to destination cluster ([Stage 3 README](3_run_rsync))

`3_run_rsync`

This final stage migrates data from the source PVs to the target PVs. In order to do this, it launches Kubernetes Jobs that migrate the data.
All PVs in a namespace will be migrated in parallel, namespaces will be done synchroneously.

*Note*: This stage __requires__ that the applications connected to the source PVCs are shut down during the migration phase. Only then, you will be sure to have a consistent data migration.

After this step, your applications will need to be re-configured to use the new PVCs. The new PVCs will have the same name as the source PVCs, but with `-ocs` appended.

### 6. Running the PVC migration

1. Run steps in: [1_pvc_data_gen/README.md](1_pvc_data_gen)
1. Run steps in: [2_pvc_destination_gen/README.md](2_pvc_destination_gen)
1. Run steps in: [3_run_rsync/README.md](3_run_rsync)
