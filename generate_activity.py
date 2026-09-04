import os
import json
import math
import urllib.request
from datetime import datetime, timezone


USERNAME = "imandeepduhan"
TOKEN = os.environ["GITHUB_TOKEN"]


# =========================================================
# GET GITHUB ACTIVITY
# =========================================================

now = datetime.now(timezone.utc)
start = datetime(now.year, 1, 1, tzinfo=timezone.utc)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

body = json.dumps({
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": start.isoformat(),
        "to": now.isoformat()
    }
}).encode()


request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=body,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-activity"
    }
)


with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())


data = result["data"]["user"]["contributionsCollection"]


commits = data["totalCommitContributions"]
issues = data["totalIssueContributions"]
pull_requests = data["totalPullRequestContributions"]
reviews = data["totalPullRequestReviewContributions"]


total = commits + issues + pull_requests + reviews


if total == 0:

    code_review = 0
    issues_percentage = 0
    pull_requests_percentage = 0
    commits_percentage = 0

else:

    code_review = round(reviews * 100 / total)
    issues_percentage = round(issues * 100 / total)
    pull_requests_percentage = round(pull_requests * 100 / total)
    commits_percentage = round(commits * 100 / total)


    # Make total exactly 100
    difference = 100 - (
        code_review
        + issues_percentage
        + pull_requests_percentage
        + commits_percentage
    )

    percentages = [
        code_review,
        issues_percentage,
        pull_requests_percentage,
        commits_percentage
    ]

    largest = percentages.index(max(percentages))
    percentages[largest] += difference

    code_review = percentages[0]
    issues_percentage = percentages[1]
    pull_requests_percentage = percentages[2]
    commits_percentage = percentages[3]


# =========================================================
# GRAPH SETTINGS
# =========================================================

width = 700
height = 400

cx = 470
cy = 200

radius = 115


def point(angle, value):

    r = radius * value / 100

    x = cx + math.cos(angle) * r
    y = cy + math.sin(angle) * r

    return x, y


# Top → Code review
# Right → Issues
# Bottom → Pull requests
# Left → Commits

angles = [
    -math.pi / 2,
    0,
    math.pi / 2,
    math.pi
]


values = [
    code_review,
    issues_percentage,
    pull_requests_percentage,
    commits_percentage
]


points = []

for angle, value in zip(angles, values):

    x, y = point(angle, value)

    points.append(f"{x:.1f},{y:.1f}")


polygon = " ".join(points)


# =========================================================
# SVG
# =========================================================

svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<!-- Background -->

<rect
    width="100%"
    height="100%"
    rx="12"
    fill="#15191e"
    stroke="#3b424a"
    stroke-width="1"/>


<!-- Title -->

<text
    x="35"
    y="45"
    fill="#f0f6fc"
    font-size="18"
    font-family="Arial, sans-serif">
    Activity overview
</text>


<!-- Vertical axis -->

<line
    x1="{cx}"
    y1="{cy-radius}"
    x2="{cx}"
    y2="{cy+radius}"
    stroke="#39d353"
    stroke-width="3"/>


<!-- Horizontal axis -->

<line
    x1="{cx-radius}"
    y1="{cy}"
    x2="{cx+radius}"
    y2="{cy}"
    stroke="#39d353"
    stroke-width="3"/>


<!-- Green activity shape -->

<polygon
    points="{polygon}"
    fill="#39d353"
    fill-opacity="0.28"
    stroke="#39d353"
    stroke-width="3"/>


<!-- Center -->

<circle
    cx="{cx}"
    cy="{cy}"
    r="5"
    fill="#39d353"/>


<!-- =====================================================
     CODE REVIEW - TOP
     ===================================================== -->

<text
    x="{cx}"
    y="72"
    text-anchor="middle"
    fill="#8b949e"
    font-size="14"
    font-family="Arial, sans-serif">
    {code_review}%
</text>

<text
    x="{cx}"
    y="93"
    text-anchor="middle"
    fill="#8b949e"
    font-size="13"
    font-family="Arial, sans-serif">
    Code review
</text>


<!-- =====================================================
     ISSUES - RIGHT
     ===================================================== -->

<text
    x="{cx+140}"
    y="{cy-6}"
    fill="#8b949e"
    font-size="14"
    font-family="Arial, sans-serif">
    {issues_percentage}%
</text>

<text
    x="{cx+140}"
    y="{cy+15}"
    fill="#8b949e"
    font-size="13"
    font-family="Arial, sans-serif">
    Issues
</text>


<!-- =====================================================
     PULL REQUESTS - BOTTOM
     ===================================================== -->

<text
    x="{cx}"
    y="{cy+140}"
    text-anchor="middle"
    fill="#8b949e"
    font-size="14"
    font-family="Arial, sans-serif">
    {pull_requests_percentage}%
</text>

<text
    x="{cx}"
    y="{cy+161}"
    text-anchor="middle"
    fill="#8b949e"
    font-size="13"
    font-family="Arial, sans-serif">
    Pull requests
</text>


<!-- =====================================================
     COMMITS - LEFT
     ===================================================== -->

<text
    x="{cx-140}"
    y="{cy-6}"
    text-anchor="end"
    fill="#8b949e"
    font-size="14"
    font-family="Arial, sans-serif">
    {commits_percentage}%
</text>

<text
    x="{cx-140}"
    y="{cy+15}"
    text-anchor="end"
    fill="#8b949e"
    font-size="13"
    font-family="Arial, sans-serif">
    Commits
</text>


</svg>
"""


# =========================================================
# SAVE
# =========================================================

with open(
    "activity-overview.svg",
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


print("===================================")
print("Activity overview updated!")
print("===================================")

print(f"Code review    : {code_review}%")
print(f"Issues         : {issues_percentage}%")
print(f"Pull requests  : {pull_requests_percentage}%")
print(f"Commits        : {commits_percentage}%")
