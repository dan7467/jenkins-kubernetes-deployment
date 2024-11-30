pipeline {
    environment {
        dockerimagename = 'dan7467/jobhaven-app'
        dockerImage = ''
    }
    agent any
    stages {
        // stage('Checkout Source') {
        //     steps {
        //         git 'https://github.com/dan7467/jenkins-kubernetes-deployment.git'
        //     }
        // }
        // testing a solution to the pipeline problem:
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM', 
                    branches: [[name: '*/main']], // Change to '*/master' or your branch
                    userRemoteConfigs: [[
                        url: 'https://github.com/dan7467/jenkins-kubernetes-deployment.git',
                        credentialsId: 'github-credentials' // Replace with your credentials ID
                    ]]
                ])
            }
        }
        stage('Build image') {
            steps {
                script {
                    dockerImage = docker.build dockerimagename
                }
            }
        }
        stage('Pushing Image') {
            environment {
                registryCredential = 'dockerhub-credentials'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', registryCredential) {
                        dockerImage.push('latest')
                    }
                }
            }
        }
        stage('Deploying app container to Kubernetes') {
            steps {
                script {
                    kubernetesDeploy(configs: 'deployment.yaml',
                                        'service.yaml')
                }
            }
        }
    }
}
