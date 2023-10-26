#!/usr/bin/env bash

docker build ./auth/ -t dhruvsha256/auth:latest
docker build ./converter/ -t dhruvsha256/converter:latest
docker build ./gateway/ -t dhruvsha256/gateway:latest

kubectl delete -f ./rabbit/manifests, kubectl apply -f ./rabbit/manifests
kubectl delete -f ./mongodb/manifests, kubectl apply -f ./mongodb/manifests
kubectl delete -f ./auth/manifests/, kubectl apply -f ./auth/manifests/
kubectl delete -f ./converter/manifests, kubectl apply -f ./converter/manifests
kubectl delete -f ./gateway/manifests, kubectl apply -f ./gateway/manifests
