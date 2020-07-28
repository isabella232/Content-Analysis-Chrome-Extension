const functionUrl = "https://political-leaning-article.azurewebsites.net/api/HttpTrigger"

var analysisChart = new Chart(document.getElementById('analysisChart'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [{ 
            data: [],
            label: "Positive",
            borderColor: "green",
            fill: false
        }, { 
            data: [],
            label: "Negative",
            borderColor: "red",
            fill: false
        }, { 
            data: [],
            label: "Neutral",
            borderColor: "blue",
            fill: false
        }]
    },
    options: {
        title: {
            display: true,
            text: 'Sentiment Analysis'
        }, 
    }
});

var counter = 0;
var continueRunning = true;

var positiveTotal = 0;
var negativeTotal = 0;
var neutralTotal = 0;

var aslTotal = 0;
var aswTotal = 0;
var scoreTotal = 0;

var typeArray = ["sentiment", "difficulty"]
var typeIndex = 0

var analyticsButton = document.getElementById("analyticsButton").addEventListener("click", getCurrentUrl);
var switchButton = document.getElementById("switchButton").addEventListener("click", switchAnalysis);

function resetValues() {
    counter = 0;
    continueRunning = true;

    positiveTotal = 0;
    negativeTotal = 0;
    neutralTotal = 0;

    aslTotal = 0;
    aswTotal = 0;
    scoreTotal = 0;

    analysisChart.data.labels = []
    analysisChart.data.datasets[0].data = []
    analysisChart.data.datasets[1].data = []
    analysisChart.data.datasets[2].data = []

    analysisChart.update();
}

function switchAnalysis() {
    if (typeArray[typeIndex].localeCompare("sentiment") == 0) {
        switchToDifficulty();
    } else if (typeArray[typeIndex].localeCompare("difficulty") == 0) {
        switchToSentiment();
    }
    updateTypeIndex();
}

function updateTypeIndex() {
    var typeLength = typeArray.length;
    typeIndex++;
    if (typeIndex == typeLength){
        typeIndex = 0;
    }
}

function switchToSentiment(){
    analysisChart.data.datasets[0].label = "Positve";
    analysisChart.data.datasets[1].label = "Negative";
    analysisChart.data.datasets[2].label = "Neutral";
    analysisChart.options.title.text = 'Sentiment Analysis';
    document.querySelector('#analyticsButton').innerText = 'Check Sentiment!';
    resetValues();
}
// change structure in the future to be more object orientated, too rigid rn
function switchToDifficulty(){
    analysisChart.data.datasets[0].label = "ASL";
    analysisChart.data.datasets[1].label = "ASW";
    analysisChart.data.datasets[2].label = "Difficulty Score";
    analysisChart.options.title.text = 'Text Difficulty Analysis';
    document.querySelector('#analyticsButton').innerText = 'Check Difficulty!';
    resetValues();
}

function getCurrentUrl() {
    resetValues();
    var url = document.getElementById('urlPlaceholder').value;
    alertFunction(url, typeArray[typeIndex]);
    // chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    //     let url = tabs[0].url;
    //     alertFunction(url, type);
    // }); 

    // use for extension
    
}

async function alertFunction(url, type){
    const proxyurl = "https://cors-anywhere.herokuapp.com/";
    var currentUrl = "?name=".concat(url);
    while (continueRunning){
        var cycle = "&cycle=".concat(counter);
        const response = await fetch(proxyurl + functionUrl + currentUrl + cycle);
        const jsonData = await response.json();
        // figure out how to deal with bug - when extension runs on chrome://extensions, returns empty json 
        if (!jsonData.continue) {
            continueRunning = false;
        } else if (type.localeCompare("sentiment") == 0) {
            counter++;
            updateSentimentData(jsonData);
            updateSentimentChart(counter);
        } else if (type.localeCompare("difficulty") == 0) {
            counter++;
            updateDifficultyData(jsonData);
            updateDifficultyChart(counter);
        } else {
            continueRunning = false;
        }
    }
    giveResults(type, counter);
}

function updateSentimentChart(counter) {
    analysisChart.data.labels.push(counter);

    analysisChart.data.datasets[0].data.push(positiveTotal/counter);
    analysisChart.data.datasets[1].data.push(negativeTotal/counter);
    analysisChart.data.datasets[2].data.push(neutralTotal/counter);

    analysisChart.update();
}

function updateSentimentData(jsonData) {
    positiveTotal += jsonData.sentiment_analysis.positive;
    negativeTotal += jsonData.sentiment_analysis.negative;
    neutralTotal += jsonData.sentiment_analysis.neutral;
}

function updateDifficultyChart(counter) {
    analysisChart.data.labels.push(counter);
    analysisChart.data.datasets[0].data.push(aslTotal/counter);
    analysisChart.data.datasets[1].data.push(aswTotal/counter);
    analysisChart.data.datasets[2].data.push(scoreTotal/counter);

    analysisChart.update();
}

function updateDifficultyData(jsonData) { 
    scoreTotal += jsonData.difficulty_analysis.flesch_reading_score;
    aslTotal += (jsonData.difficulty_analysis.asl * 1.015);
    aswTotal += (jsonData.difficulty_analysis.asw * 84.6);
}

function giveResults(type, counter){
    if (type.localeCompare("sentiment") == 0){
        updateSentimentChart(counter);
        document.getElementById("p").innerHTML = "Final Result: ".concat(getSentiment());
    } else if (type.localeCompare("difficulty") == 0){
        updateDifficultyChart(counter);
        document.getElementById("p").innerHTML = "Final Result: ".concat(getDifficulty());
    }
}

function getSentiment() {
    if (checkForMixed()) {
        return "Mixed"
    } else if (positiveTotal > negativeTotal && positiveTotal > neutralTotal) {
        return "Positive"
    } else if (negativeTotal > positiveTotal && negativeTotal > neutralTotal) {
        return "Negative"
    } else {
        return "Neutral"
    }
}

function checkForMixed() {
    var count = counter;
    return (positiveTotal/count < 0.40) && (neutralTotal/count < 0.40) && (negativeTotal/count < 0.40)
}

function getDifficulty() {
    var count = counter + 1;
    var rating = scoreTotal/count
    if (rating > 90) {
        return "Very Easy"
    } else if (rating > 70) {
        return "Easy"
    } else if (rating > 50) {
        return "Average"
    } else if (rating > 30) {
        return "Difficult"
    } else {
        return "Very Difficult"
    }
}