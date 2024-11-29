pipeline {
    environment {
        dockerimagename = 'nervous_wozniak/jobhaven-app'
        dockerImage = ''
    }
    agent any
    stages {
        stage('Checkout Source') {
            steps {
                git 'https://github.com/dan7467/jenkins-kubernetes-deployment.git'
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
