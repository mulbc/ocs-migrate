# Stage 2: pvc-destination-gen

This playbook takes the input from [Stage 1](../1_pvc_data_gen) and creates PVC OpenShift resources in destination cluster.

## Stage 2

This is the final stage where `ocs-migrate` will read the output from `Stage 1` to create PVCs on the destination cluster.
Storage Classes will be used based on the storage class mapping or pick the ceph-rbd storage class if nothing matches.

## Usage

1. Create your own copy of vars file

    ```bash
    cp vars/storage-class-mappings.yml.example vars/storage-class-mappings.yml
    ```

1. Set storage class mappings in `vars/storage-class-mappings.yml`, following directions in [sc-selection.md](../docs/sc-selection.md)

    ```yaml
    mig_storage_class_mappings:
    thin_RWO: ocs_storagecluster-ceph-rbd
    gp2_RWO: ocs-storagecluster-ceph-rbd
    nfs_RWX: ocs-storagecluster-cephfs
    ```

1. Run `Stage 2`

    ```bash
    ansible-playbook pvc-destination-gen.yml
    ```

1. Verify that PVCs are created on destination

    ```bash
    oc get pvc -n sample-namespace
    ```

1. Move on to [Stage 3](../3_run_rsync)
