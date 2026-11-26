pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Validate Compose Configuration') {
            steps {
                sh 'docker compose config -q'
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh 'docker compose run --rm --no-deps notification-service pytest -q'
            }
        }

        stage('Build and Deploy') {
            steps {
                sh 'docker compose up -d --build'
            }
        }

        stage('Smoke Tests') {
            steps {
                sh '''
                    sleep 10
                    curl -fsS http://localhost:8000/health
                    curl -fsS http://localhost:5000/health
                    curl -fsS http://localhost:9090/-/ready
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose ps || true'
        }
    }
}
