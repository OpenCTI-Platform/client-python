#!/bin/sh

set -x
if [[ -z "$1" || -z "$2" || -z "$3" || -z "$4" ]]
then
    echo "This scripts requires 3 paramaters: branch_name, PR_number, workspace and github_token"
    exit 1
fi

PR_BRANCH_NAME=$1
PR_NUMBER=$2
WORKSPACE=$3
GITHUB_TOKEN=$4

echo "[MULTI-REPO] Starting with PR_BRANCH_NAME=${PR_BRANCH_NAME}, PR_NUMBER=${PR_NUMBER}, WORKSPACE=${WORKSPACE}."
export GH_TOKEN="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"
export GH_FORCE_TTY="100%"
cd ${WORKSPACE}

ls

gh auth login --with-token ${GITHUB_TOKEN}
gh pr list

exit 0
gh repo set-default https://github.com/OpenCTI-Platform/client-python

#Check current PR to see if label "multi-repository" is set
IS_MULTI_REPO=$(gh pr view ${PR_NUMBER} --json labels | grep -c "multi-repository")
if [[ ${IS_MULTI_REPO} -eq 1 ]]
then

    OPENCTI_BRANCH=${PR_BRANCH_NAME}
    echo "[MULTI-REPO]  Multi repository PR, looking for opencti related branch"
    if [[ $(echo ${PR_BRANCH_NAME} | cut -d "/" -f 1) == "opencti" ]]
    then
        #remove opencti prefix when present for backward compatibility
        OPENCTI_BRANCH=$(echo ${PR_BRANCH_NAME} | cut -d "/" -f2-)
    fi
    echo "[MULTI-REPO] OPENCTI_BRANCH is ${OPENCTI_BRANCH}"
    gh repo clone https://github.com/OpenCTI-Platform/opencti /tmp/opencti
    cd /tmp/opencti

    # search for the first opencti PR that matches OPENCTI_BRANCH
    gh repo set-default https://github.com/OpenCTI-Platform/opencti
    gh pr list --label "multi-repository" > multi-repo-prs.txt
    OPENCTI_PR_NUMBER=$(cat multi-repo-prs.txt | grep ${OPENCTI_BRANCH} | head -n 1 | awk '{print $1}')

    if [[ -z "${OPENCTI_PR_NUMBER}" ]]
    then
        echo "[MULTI-REPO] Found a PR in opencti with number ${OPENCTI_PR_NUMBER}, using it."
        gh pr checkout ${OPENCTI_PR_NUMBER}
    fi
    
else
    echo "[MULTI-REPO] NOT multi repo, cloning opencti:master"
    gh repo clone https://github.com/OpenCTI-Platform/opencti /tmp/opencti
fi

cd /tmp/opencti
echo "Using opencti on branch:"
git branch --show-current
cd ${WORKSPACE}