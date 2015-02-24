//
//  application.js
//  fcc
//
//  Created by Jay Contonio on 2011-02-15.
//


/*********************
//* jQuery Multi Level CSS Menu #2- By Dynamic Drive: http://www.dynamicdrive.com/
//* Last update: Nov 7th, 08': Limit # of queued animations to minmize animation stuttering
//* Menu avaiable at DD CSS Library: http://www.dynamicdrive.com/style/
*********************/
//Specify full URL to down and right arrow images (23 is padding-right to add to top level LIs with drop downs):
var arrowimages={down:['downarrowclass', 'images/down.gif', 23], right:['rightarrowclass', 'images/right.gif']}
var jqueryslidemenu={
animateduration: {over: 200, out: 100}, //duration of slide in/ out animation, in milliseconds
buildmenu:function(menuid, arrowsvar){
	jQuery(document).ready(function($){
		var $mainmenu=$("#"+menuid+" .widget .widgetContent > ul")
		var $headers=$mainmenu.find("ul").parent()
		$headers.each(function(i){
			var $curobj=$(this)
			var $subul=$(this).find('ul:eq(0)')
			this._dimensions={w:this.offsetWidth, h:this.offsetHeight, subulw:$subul.outerWidth(), subulh:$subul.outerHeight()}
			this.istopheader=$curobj.parents("ul").length==1? true : false
			$subul.css({top:this.istopheader? this._dimensions.h+"px" : 0})
			$curobj.hover(
				function(e){
					var $targetul=$(this).children("ul:eq(0)")
					this._offsets={left:$(this).offset().left, top:$(this).offset().top}
					var menuleft=this.istopheader? 0 : this._dimensions.w
					menuleft=(this._offsets.left+menuleft+this._dimensions.subulw>$(window).width())? (this.istopheader? -this._dimensions.subulw+this._dimensions.w : -this._dimensions.w) : menuleft
					if ($targetul.queue().length<=1) //if 1 or less queued animations
						$targetul.css({ width:this._dimensions.subulw+'px'}).show(jqueryslidemenu.animateduration.over)
				},
				function(e){
					var $targetul=$(this).children("ul:eq(0)")
					$targetul.hide(jqueryslidemenu.animateduration.out)
				}
			) //end hover

			$curobj.keydown(
				function(e){
					if (e.which == '38') { //up arrow
						e.preventDefault();
						$mainmenu.find('ul').hide(jqueryslidemenu.animateduration.out);
					}

					if (e.which == '40') { //down arrow
						e.preventDefault();
						$mainmenu.find('ul').hide(jqueryslidemenu.animateduration.out);

						var $targetul=$(this).children("ul:eq(0)")
						this._offsets={left:$(this).offset().left, top:$(this).offset().top}
						var menuleft=this.istopheader? 0 : this._dimensions.w
						menuleft=(this._offsets.left+menuleft+this._dimensions.subulw>$(window).width())? (this.istopheader? -this._dimensions.subulw+this._dimensions.w : -this._dimensions.w) : menuleft
						if ($targetul.queue().length<=1) //if 1 or less queued animations
							$targetul.css({left:menuleft+"px", width:this._dimensions.subulw+'px'}).slideDown(jqueryslidemenu.animateduration.over);
					}

				}
			) //end keydown
		}) //end $headers.each()
		$mainmenu.find("ul").css({display:'none', visibility:'visible'})
	}) //end document.ready
}
}
//build menu with ID="myslidemenu" on page:
jqueryslidemenu.buildmenu("nav", arrowimages)


/*
 * -- Sticky Nav Window Scrolling --
 */
function getScroll()
{
	var pageY;
	if(typeof(window.pageYOffset)=='number') {
		pageY=window.pageYOffset;
	} else {
		pageY=document.documentElement.scrollTop;
	}
	return parseInt(pageY);
}


function getOffset()
{
	var pageOffset;
	pageOffset = parseInt($("#navBg").offset().top) - 24;
	return pageOffset;
}


/**
 * Shows the Display Options menu at the top of the page
 */
function showhideDisplayOption() {
	if ($('#displayOptionPanel').css('display') == 'block') {
		$('#displayOptionPanel').slideUp();
	} else {
		$('#displayOptionPanel').slideDown();
	}
}



/*
 * -- Talk to us Button --
 */
function initTalkToUs()
{
	$('#btnTalkToUs').click(function(e) {
		e.preventDefault();

		// If this is IE 7, just have the click toggle
		// Blaming this bug on a two year old version of jQuery we can't upgrade because of Drupal
		// Thanks Drupal
		if (!jQuery.support.cssFloat)
		{
			if ($('.actioncenter').hasClass('active')) {
				$('#actionbar #navTalkToUs').hide();
				$('#actionbar .actioncenter').removeClass('active');
			} else {
				$('#actionbar #navTalkToUs').slideDown();
				$('#actionbar .actioncenter').addClass('active');
			}
			return;
		}

		// Slide the menu down
		$('#actionbar #navTalkToUs').slideDown();
		$('#actionbar .actioncenter').addClass('active');

		// Add a mouseOut event to hide navTalkToUs
		$('.actioncenter').mouseleave(function(e) {
			$('#actionbar #navTalkToUs').slideUp('medium', function() {
				$('#actionbar .actioncenter').removeClass('active');
			});
			$(this).unbind('mouseleave');
		});
	});
}



/*
 * -- Enables tabs on pages using generic tab markup --
 */
/*
	TODO Turn this into a jquery plugin. Document the markup.
*/
function initPageTabs()
{
	var $divToShow, $tabContainer = $('.tabbedContent');
	if ($tabContainer.length > 0)
	{
		$tabContainer.each(function(i) {
			var $tabs = $(this).find('.dataTabs').find('a');
			var $tabbedContent = $(this).find('.dataContent');
			$tabbedContent.hide();
			$($tabbedContent[0]).show();
			// Set the click events on the tab A's
			$tabs.click(function(e) {
				e.preventDefault();
				$tabs.parent().removeClass('selected');
				$(this).parent().addClass('selected');
				var $divToShow = $($(e.target).attr('href'));
				$tabbedContent.hide();
				$divToShow.show();
			});
		});
	}
}


/*
 * -- Handles the checkbox dropdowns for the megafilter --
 */
function initFilterDropdowns()
{
	if ($('.checkboxDropdown'))
	{
		$('.checkboxDropdown .dropdownTitle').each(function(i) {
			$(this).click(function() {

				if ($(this).hasClass('activeMenu'))
				{
					resetFilterDropdowns();
					return false;
				}

				// Set the active menu
				$(this).addClass('activeMenu');
				$(this).parent().addClass('activeDropdown');
				$('.dropdownMenu').hide();
				// If the dropdown is too far to the right and is going to cover the Apply Filter button, make it open to the left
				if ($(this).parent().offset().left >= 500)
				{
					$($(this).parent()).find('.dropdownMenu').css({
						'left': '-192px',
						'border-top-left-radius': '6px'
					});
				}
				$($(this).parent()).find('.dropdownMenu').show();

				var mouseOverActiveElement = true;

				// Clicking outside the dropdown hides the dropdown
				$(window).click(function() {
					if ($('.activeDropdown:visible') && mouseOverActiveElement === false)
					{
						resetFilterDropdowns();
					}
				});

				$('.activeDropdown').mouseover(function() {
					mouseOverActiveElement = true;
				});
				$('.activeDropdown').mouseout(function() {
					mouseOverActiveElement = false;
				});

			});
		});
	}
}

/*
 * -- Clears megafilter form --
 */
function clearForm(oForm) {

  var elements = oForm.elements;
  oForm.reset();

  for(i=0; i<elements.length; i++) {
	field_type = elements[i].tagName.toLowerCase();
		switch(field_type) {
			case "text":
				elements[i].value = elements[i].defaultValue;
			case "password":
			case "textarea":
				elements[i].value = elements[i].defaultValue;
				break;
		    case "hidden":
				elements[i].value = elements[i].defaultValue;
			break;
			case "radio":
				if (elements[i].checked) {
					elements[i].checked = 1;
				}
				break;
			case "checkbox":
				if (elements[i].checked) {
					elements[i].checked = false;
				}
				break;

			case "select-one":
			case "select-multi":
		        	elements[i].selectedIndex = 0;
				break;
			default:
				break;
		}
    }
}

function resetFilterDropdowns()
{
	$('.dropdownMenu').hide();
	$('.activeMenu').removeClass('activeMenu');
	$('.activeDropdown').removeClass('activeDropdown');
	$(window).unbind('click');
}



/*
 * -- Utility Functions --
 */

/*
 * Takes an input element and clears it's value on focus. If no change occurs to the value then the original one is put back
 * @param {Object} input Text input element
 */
function clearInputValue(input)
{
	var originalValue = $(input).val();
	$(input).val('');
	$(input).blur(function() {
		if($(this).val() == '') {
			$(this).val(originalValue);
		} else {
			$(this).unbind('blur');
		}
	});
}


function hideOverlayLabels(formItem)
{
	if($(formItem).val() != '')
	{
		var id = $(formItem).attr('id');
		$('label[for=' + id + ']').hide();
	}
}

/*
 *	TODO Verify we even need these
 */
function trim(stringToTrim) {
	return stringToTrim.replace(/^\s+|\s+$/g,"");
}


function ltrim(stringToTrim) {
	return stringToTrim.replace(/^\s+/,"");
}


function rtrim(stringToTrim) {
	return stringToTrim.replace(/\s+$/,"");
}


/**
 * Log to the console without breaking anything
 */
window.log = function() {
	log.history = log.history || [];   // store logs to an array for reference
	log.history.push(arguments);
	if (this.console)
	{
	  console.log( Array.prototype.slice.call(arguments) );
	}
}

jQuery.expr[':'].Contains = function(a, i, m) {
  return jQuery(a).text().toUpperCase()
	  .indexOf(m[3].toUpperCase()) >= 0;
};
jQuery.expr[':'].contains = function(a, i, m) {
  return jQuery(a).text().toUpperCase()
	  .indexOf(m[3].toUpperCase()) >= 0;
};


/**
 * Initiailization
 */
$(document).ready(function() {

	// Remove the nojs class from the body
	$('body').removeClass('nojs');

	initTalkToUs();
	initFilterDropdowns();

	// Setup the sticky navigation
	var nav = $('#stickynav');
	var the_window = $(window);
	var topmost_point = nav.offset().top;

	$("#stickynav").remove();
	$("#stickywrapper").remove();
	$("#actionbar").wrap('<div id="stickynav" />');
	$("#stickynav").prepend("<div id='stickywrapper'></div>");

	// Add unique id's to each footer menu
	$('#footerNavigation .widgetContent > .menu > li.expanded').each(function(i) {
		$(this).attr('id', 'footer_nav_item_' + i);
	});

	/*
		TODO Redo the homepage tabs to do the generic tab markup
	*/
	$('#homepageTabs .tabs a').click(function(e) {
		e.preventDefault();
		$('#homepageTabs #tabbedContent .tab').removeClass('activeTab');
		var divToShow = $(this).attr('href');
		$(divToShow).addClass('activeTab');
		$('#homepageTabs .tabs a').removeClass('selected');
		$(this).addClass('selected');
	});

	initPageTabs();

	window.onscroll = function()
	{
		var currentScroll = getScroll();
		var currentOffset = getOffset();
		if (currentScroll > (90 + currentOffset)) {
			$('#stickynav').css('position','fixed');
			$('#actionbar .seal').fadeOut('fast');
			$("#stickywrapper").fadeIn('fast');
		} else if (currentScroll < (90 + currentOffset)) {
			$('#stickynav').css('position','static');
			$('#actionbar .seal').fadeIn('fast');
			$("#stickywrapper").fadeOut('fast');
		}
	}

	// Add titles to every link
	$('a').each(function() {
		if ($(this).attr('title') === '') {
			$(this).attr('title', $(this).text());
		}
	});

	// Add focus selector for earlier IE's
	if (jQuery.browser.msie === true)
	{
		$('input')
			.bind('focus', function() { $(this).addClass('ieFocusHack'); })
			.bind('blur', function() { $(this).removeClass('ieFocusHack'); });
	}

	$('#displayOptionLink').click(function(e) { e.preventDefault(); showhideDisplayOption(); });

	// When a user tabs from an input field, hide the label if there is a value in the input
	$('#actionbar .form-item .form-text').blur(function(e) {
		hideOverlayLabels(this);
	});

	// Give all inputs with a class of autoClear auto-clear functionality
	$('.autoClear').each(function(i) { $(this).focus(function() { clearInputValue(this); }); });

	// Make the rulemaking topic columns all the same height
	// The layout has two columns
	$('#rulemaking_topics_container .rulemaking_topic').equalheight(2);
	$('#help_topics_list .help_topic').equalheight(2);

	// function to close the alert bar
	$('#closeAlert').click( function() {
		$('#alertBar').slideUp();
	});

	// enable content filter
	if ($('.filteredContentForm').length > 0 && $('.lookupList').length > 0 && typeof $(".filterForm").filterContent == 'function') {
		$(".filteredContentForm").filterContent('.filterContent','.lookupList');
	}

	
	//function to add class to position anchor tag contents below sticky nav when click
	$('a[name]').each( function() {
		var anchortext = $(this).html();
		$(this).addClass('anchorTag').html('&nbsp;').before(anchortext);
	});

	// code highlighting for style guide
	SyntaxHighlighter.all()

	/**
	 * Move the translation links to below the title per fcc's request
	 */
	$('.node').prepend('<ul class="translations-list links inline"></ul>');
	$('.translation-link').each(function(i,link){
		$link = $(link);
		console.log($link.parent().html())
		$($link.parent()).appendTo('.translations-list');
	});

});

