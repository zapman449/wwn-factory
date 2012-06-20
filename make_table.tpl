%#template to generate a HTML table from a list of tuples (or list of 
%#lists, or tuple of tuples or ...)
<p>The created WWNs are as follows:</p>
<table border="1">
<tr><td>Host</td><td>World Wide Node #</td><td>Fabric A Port #</td><td>Fabric B Port #</td></tr>
%for row in rows:
  <tr>
  %for col in row:
    <td>{{col}}</td>
  %end
  </tr>
%end
</table>
