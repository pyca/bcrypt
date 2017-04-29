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
        timeout(time: 5, unit: 'MINUTES') {
            if (label.startsWith("windows")) {
                bat """
                    @set PATH="C:\\Python27";"C:\\Python27\\Scripts";%PATH%
                    tox -r -e $toxenv
                """
            } else {
                ansiColor('xterm') {
                    sh "tox -r -e $toxenv --  --color=yes"
                }
            }
        }
    } finally {
        deleteDir()
    }

}

def builders = [:]
for (config in configs) {
    def label = config["label"]
    def toxenvs = config["toxenvs"]

    // We need to use a temporary variable here and then
    // bind it in the for loop so that it is properly captured
    // by the closure
    for (_toxenv in toxenvs) {
        def toxenv = _toxenv
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
