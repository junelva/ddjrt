
// https://stackoverflow.com/a/4673436
if (!String.format) {
    String.format = function(format) {
        var args = Array.prototype.slice.call(arguments, 1);
        return format.replace(/{(\d+)}/g, function(match, number) {
        return typeof args[number] != 'undefined'
            ? args[number]
            : match
        ;
        });
    };
}  

window.onload = function() {

var current_chapter = 0;
var currently_expanded = {};

// populate chapter select dialog
var sel = document.getElementById("select_chapter");
for( var i = 0; i < 81; i++ ) {
    var opt = document.createElement("option");
    // opt.id = i.toString();
    opt.value = (i + 1).toString();
    opt.innerHTML = opt.value;
    sel.appendChild(opt);
}

function expandLine(row_index, line_index) {
    // console.log(String.format("expanding {0} {1}", row_index, line_index));

    var output = document.getElementById("chapter_output");
    var expansion = output.insertRow(row_index + 1);
    expansion.className = "expansion";
    var cell = document.createElement("td");
    cell.colSpan = 3;
    cell.className = "word_list";
    expansion.appendChild(cell);

    var words = chapters[current_chapter][line_index]["words"];
    for( var i = 0; i < words.length; i++ ) {
        var word_element = document.createElement("p");
        word_element.className = "word";
        word_element.innerHTML = String.format("{0} [{1}]: {2}", words[i], definitions[words[i]]["pinyin"], definitions[words[i]]["english"]);
        cell.appendChild(word_element);
    }
}

function contractLine(row_index) {
    // console.log(String.format("contracting {0} {1}", row_index, line_index));

    var output = document.getElementById("chapter_output");
    output.deleteRow(row_index + 1);
}

function loadChapter(chapter_index) {
    var chapter_data = chapters[chapter_index];

    var output = document.getElementById("chapter_output")
    while( output.firstChild ) {
        output.removeChild(output.firstChild);
    }

    currently_expanded = {};

    var chapter_title_tr = document.createElement("tr");
    var chapter_title = document.createElement("td");
    chapter_title.className = "chapter_title";
    chapter_title.colSpan = 3;
    chapter_title.innerHTML = String.format("Chapter {0}", chapter_index + 1);
    chapter_title_tr.appendChild(chapter_title);
    output.appendChild(chapter_title_tr);

    var title_spacer = document.createElement("tr");
    title_spacer.className = "spacer";
    output.appendChild(title_spacer);

    document.getElementById("select_chapter").value = chapter_index + 1;

    for( var i = 0; i < chapter_data.length; i++ ) {
        var line_data = chapter_data[i];

        var line_element = document.createElement("tr");
        line_element.id = i.toString();
        line_element.className = "line";

        line_element.addEventListener("click", function(e) {
            var that = this;

            if( currently_expanded[that.id] == false ) {
                currently_expanded[that.id] = true;
                expandLine(that.rowIndex, that.id);
            } else {
                currently_expanded[that.id] = false;
                contractLine(that.rowIndex);
            }
        });
        
        currently_expanded[line_element.id] = false;
        
        var line_num = document.createElement("td");
        line_num.className = "num";
        line_num.innerHTML = +i + 1;
        line_num.id = i.toString();
        line_element.appendChild(line_num);

        var line_ch = document.createElement("td");
        line_ch.className = "txt";
        line_ch.innerHTML = line_data["ch"];
        line_ch.id = i.toString();
        line_element.appendChild(line_ch);

        var line_en = document.createElement("td");
        line_en.className = "txt";
        line_en.innerHTML = line_data["en"];
        line_en.id = i.toString();
        line_element.appendChild(line_en);
        
        var line_spacer = document.createElement("tr");
        line_spacer.className = "spacer";

        output.appendChild(line_element);
        output.appendChild(line_spacer);
    }
}

document.getElementById("button_left").addEventListener("click", function(e) {
    e.preventDefault();
    current_chapter = Math.max(current_chapter - 1, 0);
    loadChapter(current_chapter);
    // console.log("tried to load", current_chapter)
});

document.getElementById("button_right").addEventListener("click", function(e) {
    e.preventDefault();
    current_chapter = Math.min(current_chapter + 1, 80);
    loadChapter(current_chapter);
    // console.log("tried to load", current_chapter)
});

document.getElementById("select_chapter").addEventListener("change", function(e) {
    current_chapter = e.target.value - 1;
    loadChapter(current_chapter);
    // console.log("used select to change chapter", current_chapter);
});

loadChapter(current_chapter);
}
