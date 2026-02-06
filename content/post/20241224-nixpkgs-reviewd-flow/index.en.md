---
date: 2024-12-24T00:00:00
title: How I entered the state of flow reviewing PRs in nixpkgs
summary: 'The story of how nixpkgs-reviewd became a reality'
language: en
alsoAvailable:
discussedOn:
---

For those that don't know, I am a Linux user, specifically a NixOS user (and I
expect memes incoming about this) for over 4 years,
[2020-07-37 to be exact](https://github.com/lucasew/nixcfg/commit/10ed3d3c9ed02b97bb0d82545499a9fc51a39e63),
and eventually in the Nix world you will need to engage in nixpkgs somehow.

I have over 100 PRs there, some of them adding modules, some of them adding
packages, some maintaining packages and some failed experiments
([that some of them I don't consider exactly failed](https://github.com/lucasew/nixcfg/blob/b754398dd6e699c5bedbf0317e9661894a5f85ec/nix/nodes/bootstrap/port-alloc.nix)).

One struggle I had with reviewing PRs is being a bit too superficial, like I
can't test stuff properly. Having whiterun now (Ryzen 5600G) helped a lot
building tests because riverwood (i5 7200U) is a little too slow for builds.

From a few months to now we (the NixOS Brazil group) experimented with
implementations of GitHub Actions workflows to build stuff for us. Most of the
work came from me and [thiagokokada](https://github.com/thiagokokada). We first
wanted a way to clean up space from the GitHub Actions runtime. This is
[his implementation](https://github.com/thiagokokada/free-disk-space) and this
is
[my implementation](https://github.com/lucasew/action-i-only-care-about-nix/).
My implementation is much more aggressive and ignorant working on files
themselves because, as the name says, I only care about Nix. If it's not
strictly essential for the workflow runtime I am deleting it. He may have
tweaked it more since I visit the last time tho.

About the automatic review system, I had built, at first, a workflow that runs
in my
[dotfiles repository](https://github.com/lucasew/nixcfg/blob/master/.github/workflows/nixpkgs-review.yml),
and he
[committed to his nixpkgs fork](https://github.com/thiagokokada/nixpkgs/blob/fork/actions/nixpkgs-review.nix).
Different approaches, basically the same results.

There is nothing stolen in either repo. It's all public property :)

Then he [commented this](https://t.me/nixosbrasilofftopic/118034).

I was just entered end of year collective vacations (this is a thing here at
$WORK) and I was kinda bored looking for a side project when at home.

Seemed like a perfect fit.

At first their idea was to write a cronjob that would `getUpdates` Telegram then
react to messages, then I told them about Cloudflare Workers.

I did some stuff with Cloudflare Workers already, and I loved how fast and
responsive things are. No cold starts. At the end of the day it's all a JS
bundle. Would be fun. This was in 2024-12-19.

> Lucão é uma máquina de falar coisa aleatória e implementação duvidosa :P
> (translation: Lucão is a random talk and doubtful implementation machine :P)
> ~thiagokokada, 2024 - [Link](https://t.me/nixosbrasilofftopic/118049)

He is not wrong.

I was defending my idea like a good father of ideas would do, showing the
concerns, how the technology deals with common problems in the scope.

And I was alone because I was basically the only one that did know about this
technology, and that's when
[nixpkgs-reviewd](https://github.com/nixosbrasil/nixpkgs-reviewd) was born.

Most of the work happened in two days. Basically the challenge was the
following:

- A route handler that would treat webhooks from Telegram
- That route handler would parse Telegram commands and react accordingly and if
  the command is well formed, it would trigger a GitHub Actions workflow
  dispatch workflow with arguments from that command.
- That workflow would trigger either one or three jobs that would run
  nixpkgs-review in each target I can setup. One == only linux. Three == linux +
  darwin.
- Each job would post the result independently.

This approach had some issues, especially around spammy behavior. I needed to
iterate on this because some people got angry about that, and I am fine with it.
It was a bit rude but, let's be honest, I deserved it.

After many iterations and bug fixes the current iteration only posts two
comments. One to warn that the workflow started, so the people on the PR can get
real time information about the state of the build, and another when everything
is done, that would post a comment almost the same as the one `nixpkgs-review`
itself would post.

Yeah, there were suggestions around using multi-target `nixpkgs-review` then
setting up workflows as remote builders, but this would cause some issues like:

- Remote builders have to have ssh authentication.
- Remote builders would have to be running for as long as the slowest build is
  running.
- To connect the builders, there would need to have some kind of overlay
  networking that is fast, so they can reach each other.
- I can get a very close result with much less complexity involved.

Also, while doing this I learned a GitHub Actions thing I really loved. You can
add user-friendly summaries that appear when the workflow finishes by writing it
to `$GITHUB_STEP_SUMMARY`. This helped me to resolve the spammy behavior by
bringing the details of a run in the summary so if someone wants to know
something about the run, the workflow link is there, so you only need to visit
it.

How it helped me to achieve flow?

Nixpkgs has some patterns around the PR list.

- Most of them are [r-ryantm](https://github.com/r-ryantm) automated PRs, so I
  could only skip them unless they tag me for being a maintainer.
- There are some first time contributors that bring more out of shape PRs that
  need some iterations until buildable state is achievable.
- Other PRs may include manual bumps and _backports_, miscellaneous fixes,
  people adding update scripts to let the bot cook the next updates and stuff
  like that, and refactoring.

The flow came from the following:

- I search for PRs that are not created by _r-ryantm_ and not stale:
  `is:open is:pr -author:r-ryantm -label:"2.status: stale"`
- Open a few in new tab. I only open PRs that already have the rebuild tags in
  there.
- If it looks functionally good, I run the bot. If there is _darwin_ rebuilds I
  also run the bot with the `+darwin` flag.
- When the bot notifies me that the PR is ready I then look at the results, try
  to help debug the package and if it's alright I check if stuff is in the right
  place, commit names OK and if everything seems mergeable I try to bring more
  people to look at it either by adding the link to
  ["PRs ready for review"](https://discourse.nixos.org/t/prs-ready-for-review/3032)
  or adding the reviewers manually.
- I get an email for each round trip, and email is asynchronous communication,
  so I look when I am ready.

Note that none of the steps requires me to wait, stay on the computer and react
fast. I can put a dozen PRs to review then touch some grass.

I can do most of the work in my phone. Right now only pragmatic tests,
[like the one I did with chime](https://github.com/NixOS/nixpkgs/pull/367491),
require me to stay at the computer, and those I can queue up and when I go to
the computer those are basically all cached.

And that's it. By _dogfooding_ a tool I created based on shoulders of giants
I've never reviewed so many _nixpkgs_ PRs.

BTW Merry Christmas to you all, and I hope you have a 2025 as wonderful as 2024
was to me!
