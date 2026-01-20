---

date: 2025-09-19T00:00:00
title: "Release automation and testing on CI"
summary: "How I am doing it in my projects"
discussedOn:
  - https://lobste.rs/s/isdngh/release_automation_testing_on_ci
  - https://t.me/canaldolucao/1943
---

I am the kind of guy that feels annoyed when doing the same thing
twice by process,
like fill the same task on two places, so I often look for a way to
automate. Also, I do not like to do repetitive stuff often like checking
for dependencies on my not so active projects.

For this repetitive stuff of checking for dependencies I rely on
the renovate bot[^renovate_bot]
but often the users don't clone the project
to use the software, so I had to find a way to setup releases and
build artifacts to them. As I am using GitHub Actions because I
am on GitHub and I am most comfortable using it, mostly because
of choice inertia to be honest.

[^renovate_bot]: Renovate: [GitHub](https://github.com/renovatebot/renovate)

I may translate the renovate post from portuguese[^renovate-portuguese] to english soon.

[^renovate-portuguese]: Renovate post in portuguese: [Post](/pt/post/20250515-mantendo-projetos-atualizados/)

Going back to the release problem, what I did is to basically move it
all to an Autorelease workflow. In my GitHub, most of the projects
that are not just "Deploy to Vercel" are having that or being archived.

The specific approaches actually depend on the things used to
develop that specific software, but it's mostly the same.

Basically the repository has the following items:

- `mise.toml`: Has the toolchain versions and sometimes the
commands to build the repository.
- `renovate.json`: Renovate config file, out of the standard
often there are only some automerge rules to merge patch updates
and stuff like that. It merges automatically those cases when
CI is green by default.
- `make_release`: Changes version.txt, or some other files if
needed, to update the version of the project. Normally it's run by
CI. In some Python projects this file is inside the project main module.
- `Dockerfile`: Some of the projects package a service. This file
mostly have a standard multi-stage docker build to generate the
project's container.
- `.dockerignore` and `.gitignore`: Has the output directory of
builds and other stuff, so it doesn't get committed by the workflow. 
It sucks when it happens!
- `.github/workflows/autorelease.yaml`: The one and only workflow required.

## How the workflow is set up

I'll take the workflow from ts-proxy[^ts-proxy-repo].
I think it's one of the reference implementations and often the one that I
copy over to new projects when I am setting it up on another project, even
when the project is not made in Golang.

[^ts-proxy-repo]: ts-proxy: [GitHub](https://github.com/lucasew/ts-proxy).

```yaml
name: Autorelease

on:
  push:
    branches:
    - main
    tags:
    - '*'
  workflow_dispatch:
    inputs:
      new_version:
        description: 'New tag version'
        default: 'patch'
  schedule:
    - cron: '0 2 * * 6' # saturday 2am
jobs:
  autorelease:
    env:
      REGISTRY: ghcr.io
      IMAGE_NAME: ${{ github.repository }}
      USERNAME: ${{ github.actor }}
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
      attestations: write
      id-token: write
      pull-requests: write
    steps:

    - uses: actions/checkout@v5
    - name: Setup git config
      run: |
        git config user.name actions-bot
        git config user.email actions-bot@users.noreply.github.com

    - uses: jdx/mise-action@v3

    - name: Create Pull Request if there is new stuff from updaters
      uses: peter-evans/create-pull-request@v7
      id: pr_create
      with:
        commit-message: Updater script changes
        branch: updater-bot
        delete-branch: true
        title: "Updater: stuff changed"
        body: |
          Changes caused from update scripts

    - name: Stop if a pull request was created
      env:
        PR_NUMBER: ${{ steps.pr_create.outputs.pull-request-number }}
      run: |
        if [[ ! -z "$PR_NUMBER" ]]; then
          echo "The update scripts changed something and a PR was created. Giving up deploy." >> $GITHUB_STEP_SUMMARY
          exit 1
        fi

    - name: Build binaries
      env:
        TAG: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      run: |
        echo "::group::Build container"
        docker build -t "$TAG:latest" .
        echo "::endgroup::"

        mkdir build -p && ls && pwd

        echo "# Built targets" >> $GITHUB_STEP_SUMMARY
        export CGO_ENABLED=0
        go tool dist list | grep -v wasm | while IFS=/ read -r GOOS GOARCH; do
          echo "::group::Build $GOOS/$GOARCH"
          GOOS=$GOOS GOARCH=$GOARCH go build -v -o build/ts-proxyd-$GOOS-$GOARCH ./cmd/ts-proxyd && (echo "- $GOOS/$GOARCH" >> $GITHUB_STEP_SUMMARY) || true
          echo "::endgroup::"
        done

    - name: Make release if everything looks right
      env:
        NEW_VERSION: ${{ github.event.inputs.new_version }}
      run: |
        if [[ ! -z "$NEW_VERSION" ]]; then
          NO_TAG=1 ./make_release "$NEW_VERSION"
          echo "New version: $(cat version.txt)" >> $GITHUB_STEP_SUMMARY
          echo "RELEASE_VERSION=$(cat version.txt)" >> $GITHUB_ENV
        fi

    - name: Create release
      if: env.RELEASE_VERSION != ''
      env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAG: ${{ env.RELEASE_VERSION }}
          TITLE: Release ${{ env.RELEASE_VERSION }}
      run: |
        gh release create "$TAG" \
          --title "$TITLE" \
          --generate-notes \
          --notes-start-tag $(gh release list --limit 1 --json tagName -q .[].tagName) 

    - uses: svenstaro/upload-release-action@v2
      if: env.RELEASE_VERSION != ''
      with:
        repo_token: ${{ secrets.GITHUB_TOKEN }}
        file: build/*
        tag: ${{ env.RELEASE_VERSION }}
        overwrite: true
        file_glob: true

    - name: Login to registry
      uses: docker/login-action@v3
      if: env.RELEASE_VERSION != ''
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ env.USERNAME }}
        password: ${{ github.token }}

    - name: "Build and publish container"
      env:
        TAG: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      if: env.RELEASE_VERSION != ''
      run: |
        VERSION="$(cat version.txt)"
        docker tag "$TAG:latest" "$TAG:$VERSION"
        docker push "$TAG:$VERSION"
        docker push "$TAG:latest"

```

First things first, if you want to take a workflow like this,
you must in the project settings enable an option so GitHub Actions
can create PRs. It will not explode if you don't do that, but it's an
avoidable workflow failure. Not gonna lie, I often forget that when setting up
new projects!

As you may have noticed, this bad boy has a lot of triggers.
- The **push** triggers are for commits on the main branch, or master
if your project is older. I still have some of these out there.
The tag trigger is so the deployment of the new release happens properly
on a new release.
- The **workflow_dispatch** trigger is there so I can trigger
a new release via the web interface. If ts-proxy receives a Tailscale
update from renovate I don't want to have to ssh to somewhere to
run `./make_release patch`. I can do it all on my phone, via the
browser. By default, if I don't specify, the release will be of type patch,
like in a "x.y.z" scenario it would bump the z. It can be major, minor, patch
or a specific version but this last case I never used after I set up this
named bump system.
- The **schedule** is basically to run consistency checks to review on saturday
morning. Some projects that still use Nix would have their flakes updated
even if there is no other activity in the repository.

Now for the jobs part, there is only one. No need for more!

First, there is the **env** part, where I setup some variables to use below.

The steps part I can separate in the following phases:

- **Environment setup**: sets up Git to be able to commit the consistency check changes
and have all that is required to run the consistency checks and the build itself.
- **Consistency checks**: some programs have code generation dependencies or just
need to keep lock files up to date, this is the phase that runs those code
generation tools, this includes the Nix flake bump.
- **Pull request creation**: if the consistency check step left the Git tree in a
dirty state, this part commits this state and creates a PR, if not, the process continues.
- **Build**: this is the phase where the actual build happens, in Go projects, the
build happens both for binaries and containers. Nothing is pushed yet in this phase.
- **Conditional release**: if the workflow was launched by the user, the workflow_dispatch
route, it will run the make_release without creating a tag and create a release with an
automatically generated changelog. Also, this is the part that the artifacts and containers
are uploaded. Artifacts become release artifacts and containers are tagged and pushed. If
there is no release, the workflow skips those steps.

Now I am using mostly Mise to setup the build environment. This is not the first iteration.
I used Nix before and had good results with it, but Nix has a little annoying problem:
It forces you to go all-in. Also, it doesn't allow one to use a specific version of packages
without adding a significant amount of complexity. And as Nix is mostly Linux specific it
limits adoption of the software being built by it to other platforms. Mise doesn't have
this problem. I used it to setup the JRE on Windows for a Java program I am doing to a company,
and it worked really well. Also, the environment setup of those projects is mostly
simple enough that Mise could do it in a much simpler and faster way.

This system could be very likely ported to another CI system, and that may be a future project,
but the way GitHub Actions and Renovate works is simple enough for this to not be urgent.

And that's it. That's how I am shipping software faster and with less annoyances. Want me
to set it up for you? Let me know at lucas@lew.tec.br!
