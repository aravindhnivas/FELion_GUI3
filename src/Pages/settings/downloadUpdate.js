
export default function downloadFromGit(zipFile) {
    return new Promise((resolve, reject)=>{
        console.log("Downloading file")
        const writer = fs.createWriteStream(zipFile)
        writer.on("finish", () => {resolve(); console.log("Download completed"); } )
        const {urlZip} = versionFileJSON

        fetch(urlZip)
            .then(response => response.body)
            .then(body => {
                const reader = body.getReader();

                reader.read().then( function processFile({ done, value }) {
                    if (done) {
                        console.log("Stream complete");
                        writer.end()
                        return;
                    }

                    writer.write(value)
                    return reader.read().then(processFile);
                })
            })
            .catch(err => reject(err))

    })

}