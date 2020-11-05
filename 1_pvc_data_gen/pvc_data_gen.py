#!/bin/env python3
# -*- coding: utf-8 -*-
import json
import yaml
import urllib3
import os
import re
from kubernetes import config
from openshift.dynamic import DynamicClient
from termcolor import colored
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

script_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(script_dir, '../output')

try:
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
except Exception:
    print(colored("\n [!]", "red"), "Failed while setting up OpenShift client. Ensure KUBECONFIG is set. ")
    exit(1)


# Object serving as 'get' default for empty results
class EmptyK8sResult:
    __dict__ = {}


emptyDict = EmptyK8sResult()

# Make output dir if doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(script_dir + '/vars/pvc-data-gen.yml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

node_list = []
verified_namespaces = []

print("Running stage 1 data processing on namespaces: {}".format(data['namespaces_to_migrate']))

# Generate data for namespace-data.json
for namespace in data['namespaces_to_migrate']:
    print("Processing namespace: [{}]".format(namespace))
    v1_namespaces = dyn_client.resources.get(api_version='v1', kind='Namespace')
    try:
        ns = v1_namespaces.get(name=namespace)
        ns_out = {'namespace': namespace, 'annotations': ns.metadata.get("annotations", emptyDict).__dict__}
        verified_namespaces.append(ns_out)
    except Exception:
        print(colored("\n [!]", "red"), "v1/namespace not found: {}\n".format(namespace))

ns_data_file = os.path.join(output_dir, 'namespace-data.json')
with open(ns_data_file, 'w') as f:
    json.dump(verified_namespaces, f, indent=4)
    print(colored("[✓]", "green"), "Wrote {}".format(ns_data_file))

pvc_data = []

# Generate data for pvc-data.json and node-list.json
for namespace in verified_namespaces:
    print("Processing PVCs for namespace: [{}]".format(namespace['namespace']))

    v1_pods = dyn_client.resources.get(api_version='v1', kind='Pod')
    pod_list = v1_pods.get(namespace=namespace['namespace'])

    v1_pvcs = dyn_client.resources.get(api_version='v1', kind='PersistentVolumeClaim')
    pvc_list = v1_pvcs.get(namespace=namespace['namespace'])
    namespaced_pvcs = []
    for pvc in pvc_list.items:

        # Map pod binding and uid onto PVC data
        pvc_pod = None
        boundPodName = ''
        boundPodUid = ''
        boundPodMountPath = ''
        boundPodMountContainerName = ''
        nodeName = ''
        for pod in pod_list.items:
            volumes = pod.spec.get('volumes', "")
            if volumes == "":
                continue
            for volume in volumes:
                if volume.get('persistentVolumeClaim', {}).get('claimName', '') == pvc.metadata.name:
                    pvc_pod = pod.__dict__
                    # We need volumes[].name to get the mountPath, (mssql-vol)
                    vol_name = volume.get('name', "")
                    # Next, search through list of containers on podSpec
                    # to find one with a volumeMount we want
                    for container in pod.spec.get('containers', "[]"):
                        vol_mounts = container.get('volumeMounts', [])
                        for vol_mount in vol_mounts:
                            if vol_mount.get("name", "") == vol_name:
                                boundPodMountPath = vol_mount.get("mountPath", "")
                                boundPodMountContainerName = container.get('name', "")
                                break
                    break
            if pvc_pod is not None:
                break

        if pvc_pod is not None:
            boundPodName = pod.metadata.name
            boundPodUid = pod.metadata.get("uid", "")
            nodeName = pod.spec.get("nodeName", "")
        if nodeName != "":
            node_list.append({'name': nodeName})

        # Change Read-Only-Many access mode to Read-Write-Many
        access_modes = pvc.spec.get("accessModes", "[]")
        pvc_labels = pvc.metadata.get("labels", emptyDict).__dict__

        try:
            rox_idx = access_modes.index("ReadOnlyMany")
            access_modes[rox_idx] = "ReadWriteMany"
            # Dedupe "ReadOnlyMany"
            access_modes_deduped = []
            for mode in access_modes:
                if mode not in access_modes_deduped:
                    access_modes_deduped.append(mode)
            # Set revised Access Modes list
            access_modes = access_modes_deduped
            # Apply new label indicating access mode was replaced
            pvc_labels["cam-migration-removed-access-mode"] = "ReadOnlyMany"
        # Exception will fire if "ReadOnlyMany" not found
        except Exception:
            pass

        # Build pvc-data.json data structure
        pvc_out = {
            'pvc_name': pvc.metadata.name,
            'pvc_vol_safe_name': re.sub(r'(\.+|\%+|\/+)', '-', pvc.metadata.name),
            'pvc_namespace': pvc.metadata.namespace,
            'capacity': pvc.spec.get("resources", {}).get("requests", {}).get("storage", ""),
            'labels': pvc_labels,
            'annotations': pvc.metadata.get("annotations", emptyDict).__dict__,
            'pvc_uid': pvc.metadata.get("uid", ""),
            'storage_class': pvc.spec.get("storageClassName", ""),
            'bound': pvc.status.get("phase", ""),
            'access_modes': access_modes,
            'node_name': nodeName,
            'volume_name': pvc.spec.get("volumeName", ""),
            'bound_pod_name': boundPodName,
            'bound_pod_uid': boundPodUid,
            'bound_pod_mount_path': boundPodMountPath,
            'bound_pod_mount_container_name': boundPodMountContainerName
        }
        namespaced_pvcs.append(pvc_out)
    pvc_data.append({'namespace': namespace, 'pvcs': namespaced_pvcs})

# Write out results to pvc-data.json, node-list.json
pvc_data_file = os.path.join(output_dir, 'pvc-data.json')
with open(pvc_data_file, 'w') as f:
    ns_data = json.dump(pvc_data, f, indent=4)
    print(colored("[✓]", "green"), "Wrote {}".format(pvc_data_file))

node_data_file = os.path.join(output_dir, 'node-list.json')
with open(node_data_file, 'w') as f:
    ns_data = json.dump(node_list, f, indent=4)
    print(colored("[✓]", "green"), "Wrote {}".format(node_data_file))
