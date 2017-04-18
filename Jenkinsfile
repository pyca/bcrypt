def configs = [
    [
        label: 'windows',
        toxenvs: ['py26', 'py27', 'py33', 'py34', 'py35', 'py36'],
    ],
    [
        label: 'windows64',
        toxenvs: ['py26', 'py27', 'py33', 'py34', 'py35', 'py36'],
    ],
    [
        label: 'freebsd11',
        toxenvs: ['py27'],
    ],
]

def build(label, toxenv) {
    try {
        if (label.startsWith("windows")) {
            bat """
                @set PATH="C:\\Python27";"C:\\Python27\\Scripts";%PATH%
                tox -r -e $toxenv
            """
        } else {
            wrap([$class: 'AnsiColorBuildWrapper']) {
                sh """
                tox -r -e $toxenv --  --color=yes
                """
            }
        }
    } catch (e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        deleteDir()
    }

}

def builders = [:]
for (x in configs) {
    def label = x["label"]
    def toxenvs = x["toxenvs"]

    for (y in toxenvs) {
        def toxenv = y

        def combinedName = "${label}-${toxenv}"

        builders[combinedName] = {
            node(label) {
                stage("Checkout") {
                    checkout scm
                }
                stage(combinedName) {
                    build(label, toxenv)
                }
            }
        }
    }
}

parallel builders
