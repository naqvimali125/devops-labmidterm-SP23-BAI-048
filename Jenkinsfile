pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timeout(time: 15, unit: 'MINUTES')
    }

    triggers { githubPush() }

    environment {
        STUDENT_ID = 'SP23-BAI-048'
        IMAGE      = 'naqviali125/midterm-api:latest'
        CONTAINER  = 'midterm_api'
    }

    stages {
        stage('Fetch latest data') {
            steps {
                checkout scm
                script {
                    env.COMMIT_SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                }
                sh 'git log -1 --oneline'
                sh 'wc -l dataset/train.csv'
            }
        }

        stage('Train and build image') {
            steps {
                sh 'docker build --build-arg GIT_COMMIT=$COMMIT_SHA -t $IMAGE .'
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm $IMAGE python -m pytest -q'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker rm -f $CONTAINER || true'
                sh 'docker run -d --name $CONTAINER --restart unless-stopped -p 8000:8000 $IMAGE'
            }
        }

        stage('Verify') {
            steps {
                sh '''
                for i in $(seq 1 20); do
                  out=$(curl -s http://localhost:8000/metrics || true)
                  echo "$out"
                  if echo "$out" | grep -q "$COMMIT_SHA"; then exit 0; fi
                  sleep 3
                done
                docker logs --tail 30 $CONTAINER
                exit 1
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                        sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                        sh 'docker push $IMAGE'
                        sh 'docker logout || true'
                    }
                }
            }
        }

        stage('Cleanup') {
            steps {
                sh 'docker image prune -f || true'
            }
        }
    }

    post {
        always {
            script {
                def metrics = sh(script: 'curl -s --max-time 5 http://localhost:8000/metrics || true', returnStdout: true).trim()
                def sha = env.COMMIT_SHA ?: 'unknown'
                def muted = fileExists('/var/lib/jenkins/mute_instructor')
                def toList = muted ? 'naqvimali125@gmail.com' : 'qasimalik@gmail.com'
                def ccList = muted ? '' : 'naqvimali125@gmail.com'
                def tag = muted ? '[TEST] ' : ''
                emailext(
                    from: 'naqvimali125@gmail.com',
                    to: toList,
                    cc: ccList,
                    subject: "${tag}[${env.STUDENT_ID}] MIDTERM-${env.STUDENT_ID} build #${env.BUILD_NUMBER}: ${currentBuild.currentResult}",
                    body: "Student Reg No: ${env.STUDENT_ID}\nBuild status: ${currentBuild.currentResult}\nJob: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nCommit: ${sha}\nMetrics: ${metrics}\nBuild URL: ${env.BUILD_URL}\n"
                )
            }
        }
    }
}
