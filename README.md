# openEHR Definitions Kubernetes Operator

```sh
export OPERATOR_IMAGE_NAME=openehr-definitions-operator
export OPERATOR_IMAGE_VERSION=latest

docker build . -f Containerfile -t ${OPERATOR_IMAGE_NAME}:${OPERATOR_IMAGE_VERSION}
docker tag openehr-definitions-operator:latest localhost:5001/${OPERATOR_IMAGE_NAME}:${OPERATOR_IMAGE_VERSION}
docker push localhost:5001/${OPERATOR_IMAGE_NAME}:${OPERATOR_IMAGE_VERSION}

kubectl delete --namespace ehrbase -f deployment.yaml
kubectl apply --namespace ehrbase -f deployment.yaml



kubectl apply --namespace ehrbase -f minimal-evaluation-template-cm.yaml

kubectl apply --namespace ehrbase -f minimal-others-template-cm.yaml


# Note if the CM is long then you can't use kubectl apply but instead have to create / delete explicitly
# see https://stackoverflow.com/a/62409266
kubectl create --namespace ehrbase -f chemotheraphy-cm.yaml
kubectl patch --namespace ehrbase configmap chemotherapy -p '{"metadata": {"finalizers": []}}' --type merge

# kubectl create deployment --namespace ehrbase openehr-operator --image=kind-registry:5000/${OPERATOR_IMAGE_NAME}:${OPERATOR_IMAGE_VERSION}

kubectl port-forward --namespace ehrbase service/ehrbase 8080:8080

```
