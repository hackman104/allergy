function openLink(link)
{
    if (link == "")
        return false;

    var popup = window.open(link, '_blank');
	popupBlockerChecker.check(popup);
    return false;
}

var popupBlockerChecker = {
	check: function(popup_window){
		var _scope = this;
		if (popup_window) {
			if(/chrome/.test(navigator.userAgent.toLowerCase())){
				setTimeout(function () {
					_scope._is_popup_blocked(_scope, popup_window);
				},200);
			}else{
				popup_window.onload = function (){
					_scope._is_popup_blocked(_scope, popup_window);
				};
			}
		}else{
			_scope._displayError();
		}
	},
	_is_popup_blocked: function(scope, popup_window){
		if ((popup_window.innerHeight > 0)== false){ scope._displayError(); }
	},
	_displayError: function(){
		alert("Popup blocker is enabled! Please add this site to your exception list to enable full functionality.");
	}
};

function search(query, syncResults, asyncResults)
{
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };

    $.getJSON("/lookup", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    });
}

$(document).ready(function() {

    // Configure typeahead
    $("#q").typeahead({
        hint: false,
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                '<div>' +
                '{{name}}' +
                '</div>'
            )
        }
    });

    $("#q").on("typeahead:selected", function(eventObject, suggestion, name) {

        // Open document user selects from typeahead
        var popup2 = window.open(suggestion.link, '_blank');
		popupBlockerChecker.check(popup);
    });


    $("#request").submit(function() {
        if (!$("#request input[name=rest]").val())
        {
            alert("Please enter a restaurant name to continue");
            return false;
        }

        let store = $("#request input[name=rest]").val();

        let parameters = {
            st: store
        };

        let results;

        $.ajax({
            url: "/check",
            data: parameters,
            dataType: "json",
            async: false,
            success: function(data) {
                results = data;
            }
        });

        if (results.length > 0)
        {
            alert("That restaurant's information is already available or has already been requested!");
            return false;
        }

        else
        {
            return true;
        }
    });

});





