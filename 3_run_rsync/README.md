# Stage 3: run_rsync

This playbook takes the input from [Stage 1](../1_pvc_data_gen) and [Stage 2](../2_pvc_destination_gen) and creates a Job mounting each PVC. This Job will use rsync to copy data from the source PVC to the target PVC. Once all data is copied, the Job will reach `Completed` state.
Data is copied, so it will remain on the source until you delete it manually.

## Usage

1. Create your own copy of vars file

   ```bash
   cp vars/run-rsync.yml.example vars/run-rsync.yml
   ```

1. Set vars in `vars/run-rsync.yml`

   ```yaml
   # Destination cluster 'transfer pod' resource limits
   transfer_pod_cpu_limits: '1'
   transfer_pod_cpu_requests: '100m'
   transfer_pod_mem_limits: '1Gi'
   transfer_pod_mem_requests: '1Gi'
   ```

1. Run the stage 3 playbook

   ```bash
   ansible-playbook run-rsync.yml
   ```

   This playbook will take the input from the earlier two stages and will copy the data from the source PVCs to the target PVCs. It will copy all PVCs of a namespace in parallel, but will work on one namespace at a time.
