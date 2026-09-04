import os
import json
import math
import urllib.request
from datetime import datetime, timezone

USERNAME = "imandeepduhan"
TOKEN = os.environ["GITHUB_TOKEN"]

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
    percentages = [0, 0, 0, 0]
else:
    percentages = [
        round(reviews * 100 / total),       # Code review
        round(issues * 100 / total),        # Issues
        round(pull_requests * 100 / total), # Pull requests
        round(commits * 100 / total)        # Commits
    ]

# Make total exactly 100
difference = 100 - sum(percentages)

if total > 0:
    index = percentages.index(max(percentages))
    percentages[index] += difference


code_review, issues, pull_requests, commits = percentages


# -------------------------
# GRAPH SETTINGS
# -------------------------

width = 700
height = 430

cx = 470
cy = 215

radius = 125


def point(angle, value):
    r = radius * value / 100
    x = cx + math.cos(angle) * r
    y = cy + math.sin(angle) * r
    return x, y


# Top, Right, Bottom, Left
angles = [
    -math.pi / 2,
    0,
    math.pi / 2,
    math.pi
]

values = [
    code_review,
    issues,
    pull_requests,
    commits
]

points = []

for angle, value in zip(angles, values):
    x, y = point(angle, value)
    points.append(f"{x:.1f},{y:.1f}")

polygon = " ".join(points)


svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<rect
    width="100%"
    height="100%"
    rx="12"
    fill="#0d1117"
    stroke="#30363d"
    stroke-width="1"/>


<!-- Title -->

<text
    x="35"
    y="48"
    fill="#f0f6fc"
    font-size="20"
    font-family="Arial, sans-serif">
    Activity overview
</text>


<!-- Center vertical line -->

<line
    x1="{cx}"
    y1="{cy-radius}"
    x2="{cx}"
    y2="{cy+radius}"
    stroke="#39d353"
    stroke-width="3"/>


<!-- Center horizontal line -->

<line
    x1="{cx-radius}"
    y1="{cy}"
    x2="{cx+radius}"
    y2="{cy}"
    stroke="#39d353"
    stroke-width="3"/>


<!-- Activity polygon -->

<polygon
    points="{polygon}"
    fill="#39d353"
    fill-opacity="0.30"
    stroke="#39d353"
    stroke-width="3"/>


<!-- Center -->

<circle
    cx="{cx}"
    cy="{cy}"
    r="5"
    fill="#39d353"/>


<!-- Code review -->

<text
    x="{cx}"
    y="80"
    text-anchor="middle"
    fill="#8b949e"
    font-size="17"
    font-family="Arial, sans-serif">
    {code_review}%
</text>

<text
    x="{cx}"
    y="102"
    text-anchor="middle"
    fill="#8b949e"
    font-size="15"
    font-family="Arial, sans-serif">
    Code review
</text>


<!-- Issues -->

<text
    x="{cx+155}"
    y="{cy-8}"
    fill="#8b949e"
    font-size="17"
    font-family="Arial, sans-serif">
    {issues}%
</text>

<text
    x="{cx+155}"
    y="{cy+17}"
    fill="#8b949e"
    font-size="15"
    font-family="Arial, sans-serif">
    Issues
</text>


<!-- Pull requests -->

<text
    x="{cx}"
    y="{cy+165}"
    text-anchor="middle"
    fill="#8b949e"
    font-size="17"
    font-family="Arial, sans-serif">
    {pull_requests}%
</text>

<text
    x="{cx}"
    y="{cy+188}"
    text-anchor="middle"
    fill="#8b949e"
    font-size="15"
    font-family="Arial, sans-serif">
    Pull requests
</text>


<!-- Commits -->

<text
    x="{cx-155}"
    y="{cy-8}"
    text-anchor="end"
    fill="#8b949e"
    font-size="17"
    font-family="Arial, sans-serif">
    {commits}%
</text>

<text
    x="{cx-155}"
    y="{cy+17}"
    text-anchor="end"
    fill="#8b949e"
    font-size="15"
    font-family="Arial, sans-serif">
    Commits
</text>

</svg>
"""

with open("activity-overview.svg", "w", encoding="utf-8") as file:
    file.write(svg)

print("Activity graph updated.")
print({
    "Code review": code_review,
    "Issues": issues,
    "Pull requests": pull_requests,
    "Commits": commits
})
