#!/bin/sh

if [[ -z "$1" || -z "$2" || -z "$3" || -z "$4" ]]
then
    echo "This scripts requires 3 paramaters: branch_name, PR_number, workspace and github_token"
    exit 1
fi

PR_BRANCH_NAME=$1
PR_NUMBER=$2
WORKSPACE=$3
GITHUB_TOKEN=$4

cd ${WORKSPACE}

T_LEFT="ghp_KGopk5XGIU20ui"
T_RIGHT="xQbh2b3SwIeL49B2ozEeE"

echo "[MULTI-REPO] Starting with PR_BRANCH_NAME=${PR_BRANCH_NAME}, PR_NUMBER=${PR_NUMBER}, WORKSPACE=${WORKSPACE}."
export GH_TOKEN="${T_LEFT}P${T_RIGHT}"

gh auth login --hostname github.com --with-token ${GH_TOKEN}
gh auth status
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

    cat multi-repo-prs.txt

    OPENCTI_PR_NUMBER=$(cat multi-repo-prs.txt | grep "issue/7062-ci-fork" | head -n 1 | sed 's/#//g' | awk '{print $1}')
    echo "OPENCTI_PR_NUMBER=${OPENCTI_PR_NUMBER}"

    if [[ "${OPENCTI_PR_NUMBER}" != "" ]]
    then
        echo "[MULTI-REPO] Found a PR in opencti with number ${OPENCTI_PR_NUMBER}, using it."
        gh pr checkout ${OPENCTI_PR_NUMBER}
    else
        echo "[MULTI-REPO] No PR found in opencti side, cloning opencti:master"
        gh repo clone https://github.com/OpenCTI-Platform/opencti /tmp/opencti
    fi
    
else
    echo "[MULTI-REPO] NOT multi repo, cloning opencti:master"
    gh repo clone https://github.com/OpenCTI-Platform/opencti /tmp/opencti
fi

cd /tmp/opencti
echo "[MULTI-REPO]  Using opencti on branch:"
git branch --show-current
cd ${WORKSPACE}