# numerai_exporter

To authenticate the exporter to your Numerai account, you need to generate a Numerai API key and set it via 
the `NUMERAI_PUBLIC_ID`/`NUMERAI_SECRET` environment variables.

Create an API key at https://signals.numer.ai/account with the following scopes:

- read_submission_info
- read_user_info

## NOTE

Project currently only supports getting general Numerai metrics and Signals tournament metrics. Pull requests welcome to support other tournaments.

## DockerHub

Image available at: https://hub.docker.com/r/vftaylor/numerai_exporter

## Run using Docker

    docker run -e NUMERAI_PUBLIC_ID=<PUBLIC_ID> -e NUMERAI_SECRET=<SECRET> vftaylor/numerai_exporter:latest

## Run using Kubernetes

    ---
    apiVersion: v1
    kind: Secret
    metadata:
      name: numerai-exporter-credentials
      namespace: default
    type: Opaque
    data:
      NUMERAI_PUBLIC_ID: <PUBLIC_ID_BASE64_ENCODED>
      NUMERAI_SECRET: <SECRET_BASE64_ENCODED>
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: app
      namespace: default
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: app
      template:
        metadata:
          labels:
            app: app
        spec:
          containers:
            - name: main
              image: vftaylor/numerai_exporter:latest
              imagePullPolicy: Always
              ports:
                - name: app
                  containerPort: 8000
              env:
                - name: NUMERAI_PUBLIC_ID
                  valueFrom:
                    secretKeyRef:
                      name: numerai-exporter-credentials
                      key: NUMERAI_PUBLIC_ID
                - name: NUMERAI_SECRET
                  valueFrom:
                    secretKeyRef:
                      name: numerai-exporter-credentials
                      key: NUMERAI_SECRET
              resources:
                requests:
                  cpu: 100m
                  memory: 100Mi
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: app
      namespace: default
      labels:
        app: app
      annotations:
        "prometheus.io/scrape": "true"
        "prometheus.io/port": "8000"
    spec:
      selector:
        app: app
      ports:
        - name: app
          port: 8000
          targetPort: 8000
          protocol: TCP
      type: ClusterIP
