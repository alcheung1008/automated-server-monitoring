pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Environment File') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'webex-bot-token',
                        variable: 'WEBEX_BOT_TOKEN'
                    ),
                    string(
                        credentialsId: 'webex-room-id',
                        variable: 'WEBEX_ROOM_ID'
                    )
                ]) {
                    sh '''
                        umask 077
                        printf 'WEBEX_BOT_TOKEN=%s\\n' "$WEBEX_BOT_TOKEN" > .env
                        printf 'WEBEX_ROOM_ID=%s\\n' "$WEBEX_ROOM_ID" >> .env
                    '''
                }
            }
        }

        stage('Validate Compose Configuration') {
            steps {
                sh 'docker compose config -q'
            }
        }

	stage('Build Images') {
    	    steps {
        	sh 'docker compose build'
            }
	}

        stage('Run Unit Tests') {
            steps {
                sh '''
                    docker compose run --rm --no-deps \
                        notification-service pytest -q
                '''
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
            sh 'rm -f .env'
        }
    }
}
