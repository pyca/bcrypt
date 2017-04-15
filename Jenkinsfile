def configs = [
    [
        label: 'windows',
        toxenvs: ['py26', 'py27', 'py33', 'py34', 'py35', 'py36'],
    ],
    [
        label: 'windows64',
        toxenvs: ['py26', 'py27', 'py33', 'py34', 'py35', 'py36'],
    ],
]

def build(label, toxenv) {
    try {
        checkout scm
        if (label.startsWith("windows")) {
            bat """
                @set PATH="C:\\Python27";"C:\\Python27\\Scripts";%PATH%
                tox -r -e $toxenv
            """
        } else {
            sh """
            tox -r -e $toxenv
            """
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
                stage(combinedName) {
                    build(label, toxenv)
                }
            }
        }
    }
}

parallel builders
