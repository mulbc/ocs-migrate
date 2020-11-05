# Storage Class Selection

**Stage 2** of `ocs-migrate` is responsible for migrating PVCs resource definitions to OCS.

While migrating PVCs, `ocs-migrate` cannot automatically choose the correct StorageClass (SC) for migrated PVCs. Thus you have to map your source storage classes to the OCS storage classes yourself. As examples of such mappings:

- **RWO mode PV** storage class like `px-replicated`, `px-db` (Portworx) or `gp2` (AWS) or `thin` (VMware) typically maps to the `cephrbd` storage class
- **RWX mode PV** based on NFS storage classes typically maps to the `cephfs` storage class

Since `ocs-migrate` ___cannot___ automatically determine the desired conversion between Storage Classes. You must provide a static mapping of StorageClass names between the source and the destination cluster.

## Example mapping from `storage-class-mappings.yml`

```yml
mig_storage_class_mappings:
  thin_RWO: ocs_storagecluster-ceph-rbd
  gp2_RWO: ocs-storagecluster-ceph-rbd
  nfs_RWX: ocs-storagecluster-cephfs
```

The sample above follows this general format:

```yaml
mig_storage_class_mappings:
  <SC-NAME-ON-SOURCE>_<MODE>: <SC-NAME-ON-DESTINATION>
```

## Mapping Behavior

- If an applicable mapping is not found, `ocs-migrate` will retain the original StorageClass in the migrated PVC, which will result in a failure.
- If a PVC doesn't have any StorageClass assigned, the migrated PVC will use the `ocs_storagecluster-ceph-rbd` StorageClass on the destination.

## Required Steps for Stage 2

- Before running [Stage 2](../2_pvc_destination_gen), the StorageClass mapping must be provided in [storage-class-mappings.yml](../2_pvc_destination_gen/vars/storage-class-mappings.yml)
