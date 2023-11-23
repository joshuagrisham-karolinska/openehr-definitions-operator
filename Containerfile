FROM registry.access.redhat.com/ubi9/python-311:1-34.1699551735
ENV NAMESPACE=default
ADD src /opt/app-root/src
RUN pip install -r /opt/app-root/src/requirements.txt
CMD kopf run --namespace=${NAMESPACE} /opt/app-root/src/operator.py --verbose
