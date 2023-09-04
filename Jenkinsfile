#!/usr/bin/env groovy
def gv
def remoteHost = '3.15.140.92'
def remoteCredentials = 'aws-ubuntu'
def composePath = '/home/ubuntu/foodgram/foodgram-react-jenkins/infra/'

pipeline {
    agent any

    tools {
        nodejs 'nodejs.20'
    }

    parameters {
        booleanParam(name: 'deployFront', defaultValue: true, description: '')
        string(name: 'FRONT_VERSION', defaultValue: '', description: 'frontend docker image version', trim: true)
        booleanParam(name: 'deployBack', defaultValue: true, description: '')
        string(name: 'BACK_VERSION', defaultValue: '', description: 'backend docker image version', trim: true)
        booleanParam(name: 'executeTests', defaultValue: false, description: '')
        choice(name: 'TargetEnvironment', choices: ['DEV', 'PROD'], description: 'Where to deploy?') 
    }

stages {

        stage('init') {
            steps {
                script {
                    gv = load "script.groovy"
                    if (params.TargetEnvironment == 'DEV') {
                    remoteHost = '192.168.230.131'
                    remoteCredentials = 'vmware-ubuntu'
                    composePath = '/home/kroot/foodgram-react-jenkins/infra/'
                    } 
                }
            }
        }

        stage('echo') {
            steps {
                script {
                    echo "target environment is ${params.TargetEnvironment}"
                    echo "composePath is ${composePath}"
                    echo "remoteHost is ${remoteHost}"
                    echo "remoteCredentials is ${remoteCredentials}"                    
                    } 
                }
            }

        stage('execute tests'){
            when {
                expression { params.executeTests
                }
            }
            steps {
                script {
                    echo 'WE SHOULD HAVE WRITTEN AT LEAST ONE TEST'
                }
            }    
        }

        stage('build and deploy front'){
            when {
                expression { params.deployFront
                }
            }
            steps {
                script {
                    gv.buildImage('foodgram-frontend', "${FRONT_VERSION}", './frontend')
                    echo "deploying foodgram-frontend to ${params.TargetEnvironment}, authenticating with ${remoteCredentials} on ${remoteHost}"
                    gv.updateContainer ("${remoteHost}", "${remoteCredentials}", 'foodgram-frontend', 'kryssperer', "${params.FRONT_VERSION}", "${composePath}")
                }
            }
        }

        stage('build and deploy back'){
            when {
                expression { params.deployBack
                }
            }
            steps {
                script {
                    gv.buildImage('foodgram-backend', "${BACK_VERSION}", './backend')
                    echo "deploying foodgram-backend to ${params.TargetEnvironment}, authenticating with ${remoteCredentials} on ${remoteHost}"
                    gv.updateContainer ("${remoteHost}", "${remoteCredentials}", 'foodgram-backend', 'kryssperer',"${params.BACK_VERSION}", "${composePath}")
                }
            }
        }
    }
}