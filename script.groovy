def buildImage(imagename, imageversion, imagepath) {
    echo 'building the docker image...'
    echo "${imagename}, version ${imageversion}"
    withCredentials([usernamePassword(credentialsId: '6ec9d130-1d94-42af-9cf5-26ab651d58da', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
            sh """
                docker build ${imagepath} -t kryssperer/${imagename}:${imageversion}
                docker tag kryssperer/${imagename}:${imageversion} ${imagename}:latest
                echo $PASS | docker login -u $USER --password-stdin
                docker push kryssperer/${imagename} --all-tags
            """
    }
}

def updateContainer (host, credentials, container, repository, version, composeFileDirectory) {
    echo "connecting to ${host} to update ${container}"
    withCredentials([sshUserPrivateKey(credentialsId: "$credentials", keyFileVariable: 'KEYFILE', usernameVariable: 'USER')]) {
        script {
            sh """
            ssh -o StrictHostKeyChecking=no -i ${KEYFILE} ${USER}@${host} "sudo docker pull ${repository}/${container}:${version} && sudo docker-compose -f ${composeFileDirectory}docker-compose.production.yml up -d"
            """
        }
    }
}


return this