#!/usr/bin/perl

use strict;
use warnings;
use CGI;

use File::Spec;

my $cgi_o = CGI->new();

## Variables: DATALIB, ID, QUERY_FROM, QUERY_TO, AND STRAND
## Retrieve the variables:

my $db_root = "db";

my $datalib = $cgi_o->param('DATALIB');
my $id = $cgi_o->param('ID');
my $qry_f = $cgi_o->param('QUERY_FROM');
my $qry_t = $cgi_o->param('QUERY_TO');
my $strd = $cgi_o->param('STRAND');

## Reformat the ID according fasta
## don't letting the user use spaces

if ($id =~ m/^(.+)\s+/) {
    $id = $1;
}


## Define the header

my $header =
'<img USEMAP=#img_map WIDTH=509 HEIGHT=22 SRC="images/fastacmd_form.gif" ISMAP>
<map name=img_map>
<area shape=rect coords=2,1,48,21 href="http://www.ncbi.nlm.nih.gov">
<area shape=rect coords=419,1,459,21 href="index.html">
<area shape=rect coords=465,1,505,21 href="docs/fastacmd_help.html">
</map>
';

## Create the error and out variable:

my $err;
my $out;

## Prepare the command:

unless (defined $datalib) {
    $err = "ERROR: No -d <database> parameter was specified.";
}
else {
    $datalib = File::Spec->catfile($db_root, $datalib);
}
unless (defined $id) {
    $err = "ERROR: No -s <search_by_id> parameter was specified.";
}
else {
    if ($id =~ m/[;|>|<|,|'|"|`|:|\/|\\|*|?|!|&]/) {
	$err = "ERROR: -s ID argument has a non-valid character.";
    }
}


my $fastacmd = "fastacmd -d " . $datalib . " -s " . $id;

## Check query_from and query_to and add to the command

if (defined $qry_f && defined $qry_t && $qry_f =~ m/./ && $qry_t =~ m/./) {
    if ($qry_f !~ m/^\d+$/) {
	$err = "ERROR: QUERY_FROM parameter is not an integer.";
    }
    elsif ($qry_t !~ m/^\d+$/) {
	$err = "ERROR: QUERY_TO parameter is not an integer."
    }
    elsif ($qry_t <= $qry_f) {
	$err = "ERROR: QUERY_FROM parameter is bigger than QUERY_TO parameter."
    }
    else {

	## Add the Query_from and Query_to parameters

	$fastacmd .= " -L" . $qry_f . "," . $qry_t;
    }
}
elsif (defined $qry_f && $qry_f =~ m/./) {
    $err = "ERROR: QUERY_FROM parameter was specified but QUERY_TO is missing.";
}
elsif (defined $qry_t && $qry_t =~ m/./) {
    $err = "ERROR: QUERY_TO parameter was specified but QUERY_FROM is missing.";
}

## Check strand and add to the command

if (defined $strd && $strd =~ m/./) {
    if ($strd !~ m/^[\+|-]$/) {
	$err = "ERROR: STRAND parameter only can take + or - values."
    }
    elsif ($strd =~ m/-/) {
	$fastacmd .= " -S 2";
    }
    else {
	$fastacmd .= " -S 1";
    }
}

## Now, before run the command it will check if there are any errors:

if (defined $err) {
    $out = '<br><b>An error was detected during the program execution:</b><br>';
    $out .= "COMMAND: $fastacmd<BR>";
    $out .= "<br><b>" . $err . "</b><br>";
}
else {
    $out = `$fastacmd`;

    if ($out !~ m/^>/ && $out =~ m/.+/) {
	$err = $out;
	$out = '<br><b>COMMAND EXECUTION ERROR:</b><br>An error ';
	$out .= 'was detected for the execution of the command:<br>';
	$out .= "<br>$fastacmd<br><br>";
	$out .= $err . "<br>";
    }
    elsif ($out !~ m/^>/) {
	$err = "<br><b>No sequence was found with ID=$id</b><br><br>";
	$out = $err;
    }
}

## Finally print the results:

print $cgi_o->header(), 
      $cgi_o->start_html('fasta'); # start the HTML
if ($err =~ m/.+/) {
    print $header;
    print "<hr>";
}
print "<pre>" . $out . "</pre>";
if ($err =~ m/.+/) {
    print "<hr>";
}
print $cgi_o->end_html;            # end the HTML


1;
