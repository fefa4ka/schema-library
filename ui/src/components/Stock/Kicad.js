

export const KiCad = function (canvas, options) {
    function Exception(message) {
        this.message = message;
    }
    
  // check if canvas is usable
  if (canvas.getContext) {
      var context = canvas.getContext('2d');
  } else {
      throw new Exception("Can't get context of canvas")
  }

  // create empty options if not given as param
  if (options == null) {
      options = {};
  }

  // default colors taken form KiCAD
  var defaults = {
      'Fg': {'r': 255, 'g': 255, 'b': 255},
      'Bg': {'r': 0, 'g': 0, 'b': 0},
      'F.Cu': {'r': 132, 'g': 0, 'b': 0},
      'B.Cu': {'r': 0, 'g': 132, 'b': 0},
      'F.Adhes': {'r': 132, 'g': 0, 'b': 132},
      'B.Adhes': {'r': 0, 'g': 0, 'b': 132},
      'F.Paste': {'r': 132, 'g': 0, 'b': 0},
      'B.Paste': {'r': 0, 'g': 194, 'b': 194},
      'F.SilkS': {'r': 0, 'g': 132, 'b': 132},
      'B.SilkS': {'r': 132, 'g': 0, 'b': 132},
      'F.Mask': {'r': 132, 'g': 0, 'b': 132},
      'B.Mask': {'r': 132, 'g': 132, 'b': 0},
      'Dwgs.User': {'r': 194, 'g': 194, 'b': 194},
      'Cmts.User': {'r': 0, 'g': 0, 'b': 132},
      'Eco1.User': {'r': 0, 'g': 132, 'b': 0},
      'Eco2.user': {'r': 194, 'g': 194, 'b': 0},
      'Egde.Cuts': {'r': 194, 'g': 194, 'b': 0},
      'Margin': {'r': 194, 'g': 0, 'b': 194},
      'F.CrtYd': {'r': 132, 'g': 132, 'b': 132},
      'B.CrtYd': {'r': 0, 'g': 0, 'b': 0},
      'F.Fab': {'r': 194, 'g': 194, 'b': 0},
      'B.Fab': {'r': 132, 'g': 0, 'b': 0},
      'grid': 1.27,
      'grid_color': {'r': 132, 'g': 132, 'b': 132}
  }

  // holds the KiCAD file
  var data = {};
  // zoom level
  var zoom = 0;
  var default_zoom = 0;
  // x and y axis translation
  var move_x = 0;
  var move_y = 0;

  // fill options with defaults where no option was given by the user
  for (var key in defaults) {
      options[key] = options[key] || defaults[key];
  }

  var draw_grid = function(size) {
      // we need the center for alignment
      var center_x = canvas.width / 2;
      var center_y = canvas.height / 2;

      // find out how many dots fit in the canvas
      var dots_x = parseInt(canvas.width / size);
      dots_x += dots_x % 2;  // make it an even number
      var dots_y = parseInt(canvas.height / size);
      dots_y += dots_y % 2;  // make it an even number

      for (var x = 0; x <= dots_x; x++) {
          for (var y = 0; y <= dots_y; y++) {
              /*
              here the even numbers for x and y are important.
              draw the dots starting from the top left corner by moving the center half way left and up.
              you understand it if you stare at the code for 5 mins.
               */
              var px = (x * size + center_x) - (dots_x / 2 * size) + move_x;
              var py = (y * size + center_y) - (dots_y / 2 * size) + move_y;

              // check if the dot is in the canvas (visible)
              if (px > 0 && px < canvas.width && py > 0 && py < canvas.height) {
                  context.fillStyle = "rgba("
                      + options['grid_color']['r'] + ", "
                      + options['grid_color']['g'] + ", "
                      + options['grid_color']['b'] + ", 1)";
                  context.fillRect(px, py, 1, 1);
              }
          }
      }
  };

  var draw_fpline = function(fpline) {
      context.beginPath();
      context.strokeStyle = "rgba("
          + options[fpline['layer']]['r'] + ", "
          + options[fpline['layer']]['g'] + ", "
          + options[fpline['layer']]['b'] + ", 1)";
      context.lineWidth = fpline['width'];
      context.lineCap = 'square';
      context.moveTo(fpline['x1'], fpline['y1']);
      context.lineTo(fpline['x2'], fpline['y2']);
      context.stroke()
  };

  var draw_fpcircle = function(fpcircle) {
      context.beginPath();
      context.strokeStyle = "rgba("
          + options[fpcircle['layer']]['r'] + ", "
          + options[fpcircle['layer']]['g'] + ", "
          + options[fpcircle['layer']]['b'] + ", 1)";
      context.lineWidth = fpcircle['width'];
      context.arc(fpcircle['center_x'], fpcircle['center_y'], fpcircle['radius'], 0, 2 * Math.PI, false);
      context.stroke();
  };

  var draw_fparc = function(fparc) {
      var dx = fparc['point_x'] - fparc['center_x'];
      var dy = fparc['point_y'] - fparc['center_y'];
      var start_angle = Math.atan2(dy, dx);
      var end_angle = start_angle + fparc['angle'] * Math.PI / 180;
      context.beginPath();
      context.strokeStyle = "rgba("
          + options[fparc['layer']]['r'] + ", "
          + options[fparc['layer']]['g'] + ", "
          + options[fparc['layer']]['b'] + ", 1)";
      context.lineWidth = fparc['width'];
      context.arc(fparc['center_x'], fparc['center_y'], fparc['radius'], start_angle, end_angle, false);
      context.stroke();
  };

  var draw_fptext = function(fptext) {
      // TODO: not yet implemented
  };

  var draw_pad = function(pad) {
      if (pad['shape'] === 'circle') {
          context.beginPath();
          context.fillStyle = "rgba("
              + options['B.Mask']['r'] + ", "
              + options['B.Mask']['g'] + ", "
              + options['B.Mask']['b'] + ", 1)";
          context.arc(pad['x'], pad['y'], pad['width'] / 2, 0, 2 * Math.PI, false);
          context.fill();
      /*
      else if (pad['shape'] === 'oval') {
          // TODO: implement me!
          context.beginPath();
          context.fillStyle = "rgba("
              + options['B.Mask']['r'] + ", "
              + options['B.Mask']['g'] + ", "
              + options['B.Mask']['b'] + ", 1)";
          context.fill();
      */
      } else if (pad['shape'] === 'rect') {
          context.fillStyle = "rgba("
              + options['B.Mask']['r'] + ", "
              + options['B.Mask']['g'] + ", "
              + options['B.Mask']['b'] + ", 1)";
          context.fillRect(pad['x'] - pad['width'] / 2, pad['y'] - pad['height'] / 2, pad['width'], pad['height']);
      }

      if (pad['type'] === 'thru_hole') {
          context.beginPath();
          context.fillStyle = "rgba("
              + options['Bg']['r'] + ", "
              + options['Bg']['g'] + ", "
              + options['Bg']['b'] + ", 1)";
          context.arc(pad['x'], pad['y'], pad['drill'] / 2, 0, 2 * Math.PI, false);
          context.fill();
      } else if (pad['type'] === 'np_thru_hole') {
          // TODO: implement me!
      } else if (pad['type'] === 'smd') {
          // TODO: implement me!
      }

      if (pad['num'] !== '') {
          context.beginPath();
          context.textAlign = 'center';
          context.textBaseline = 'middle';
          context.fillStyle = "rgba("
              + options['Fg']['r'] + ", "
              + options['Fg']['g'] + ", "
              + options['Fg']['b'] + ", 1)";
          context.fillText(pad['num'], pad['x'], pad['y']);
      }
  };

  var draw_footprint = function() {
      // draw background
      context.fillStyle = "rgb("
          + options['Bg']['r'] + ", "
          + options['Bg']['g'] + ", "
          + options['Bg']['b'] + ")";
      context.fillRect(0, 0, canvas.width, canvas.height);

      // set outer boundaries of pretty file
      var left = 0;
      var top = 0;
      var right = 0;
      var bottom = 0;

      var update_dimensions = function(x, y) {
          if (parseFloat(x) < parseFloat(left)) {
              left = x;
          } else if (parseFloat(x) > parseFloat(right)) {
              right = x;
          }
          if (parseFloat(y) < parseFloat(bottom)) {
              return bottom = y;
          } else if (parseFloat(y) > parseFloat(top)) {
              return top = y;
          }
      };

      // save all lines in a list to draw them later
      var fp_lines = [];
      var fp_circles = [];
      var fp_arcs = [];
      var fp_texts = [];
      var pads = [];

      // read pretty file
      var prettylines = data.split('\n');
      for (var i = 0; i < prettylines.length; i++) {
          var m;

          var line = prettylines[i].trim();

          // check if current line is a line
          var regex_fpline = /\(fp_line \(start ([-.\d]*) ([-.\d]*)\) \(end ([-.\d]*) ([-.\d]*)\) \(layer ([.a-zA-Z]*)\) \(width ([-.\d]*)\)\)/g;
          while ((m = regex_fpline.exec(line)) !== null) {
              if (m.index === regex_fpline.lastIndex) {
                  regex_fpline.lastIndex++;
              }
              var fp_line = {
                  x1: parseFloat(m[1]),
                  y1: parseFloat(m[2]),
                  x2: parseFloat(m[3]),
                  y2: parseFloat(m[4]),
                  layer: m[5],
                  width: parseFloat(m[6])
              };
              update_dimensions(fp_line['x1'], fp_line['y1']);
              update_dimensions(fp_line['x2'], fp_line['y2']);
              fp_lines.push(fp_line);
          }

          // check if current line is an arc
          var regex_fparc = /\(fp_arc \(start ([-.\d]*) ([-.\d]*)\) \(end ([-.\d]*) ([-.\d]*)\) \(angle ([-.\d]*)\) \(layer ([.a-zA-Z]*)\) \(width ([-.\d]*)\)\)/g;
          while ((m = regex_fparc.exec(line)) !== null) {
              if (m.index === regex_fparc.lastIndex) {
                  regex_fparc.lastIndex++;
              }
              var fp_arc = {
                  center_x: parseFloat(m[1]),
                  center_y: parseFloat(m[2]),
                  point_x: parseFloat(m[3]),
                  point_y: parseFloat(m[4]),
                  radius: Math.sqrt(Math.pow(parseFloat(m[1]) - parseFloat(m[3]), 2) + Math.pow(parseFloat(m[2]) - parseFloat(m[4]), 2)),
                  angle: parseFloat(m[5]),
                  layer: m[6],
                  width: parseFloat(m[7])
              };
              update_dimensions(fp_arc['center_x'] - fp_arc['radius'], fp_arc['center_y'] - fp_arc['radius']);
              update_dimensions(fp_arc['center_x'] + fp_arc['radius'], fp_arc['center_y'] + fp_arc['radius']);
              fp_arcs.push(fp_arc);
          }

          // check if current line is a circle
          var regex_fpcircle = /\(fp_circle \(center ([-.\d]+) ([-.\d]+)\) \(end ([-.\d]+) ([-.\d]+)\) \(layer ([.\w]+)\) \(width ([.\d]+)\)\)/g;
          while ((m = regex_fpcircle.exec(line)) !== null) {
              if (m.index === regex_fpcircle.lastIndex) {
                  regex_fpcircle.lastIndex++;
              }
              var fp_circle = {
                  center_x: parseFloat(m[1]),
                  center_y: parseFloat(m[2]),
                  radius: Math.sqrt(Math.pow(parseFloat(m[1]) - parseFloat(m[3]), 2) + Math.pow(parseFloat(m[2]) - parseFloat(m[4]), 2)),
                  layer: m[5],
                  width: parseFloat(m[6])
              };
              update_dimensions(fp_circle['center_x'] - fp_circle['radius'], fp_circle['center_y'] - fp_circle['radius']);
              update_dimensions(fp_circle['center_x'] + fp_circle['radius'], fp_circle['center_y'] + fp_circle['radius']);
              fp_circles.push(fp_circle);
          }

          // check if current line is a pad
          var regex_pad = /\(pad ([\d]*) ([_a-z]*) ([a-z]*) \(at ([-.\d]*) ([-.\d]*)\) \(size ([.\d]*) ([.\d]*)\) \(drill ([.\d]*)\) \(layers ([\w\d\s.*]*)\)\)/g;
          while ((m = regex_pad.exec(line)) !== null) {
              if (m.index === regex_pad.lastIndex) {
                  regex_pad.lastIndex++;
              }
              var num;
              if (m[1] === '""') {
                  num = '';
              } else {
                  num = m[1];
              }
              var pad = {
                  num: num,
                  type: m[2],
                  shape: m[3],
                  x: parseFloat(m[4]),
                  y: parseFloat(m[5]),
                  width: parseFloat(m[6]),
                  height: parseFloat(m[7]),
                  drill: parseFloat(m[8]),
                  layers: m[9].split(' ')
              };
              update_dimensions(pad['x'] - pad['width'] / 2, pad['y'] - pad['height'] / 2);
              update_dimensions(pad['x'] + pad['width'] / 2, pad['y'] + pad['height'] / 2);
              pads.push(pad);
          }

          // check if current line is a text
          var regex_fptext = /\(fp_text (reference|value|user) (.)+ \(at ([-.\d]+) ([-.\d]+)( [-.\d]+)?\) \(layer ([.\w\d])+\)/g;
          while ((m = regex_fptext.exec(line)) !== null) {
              if (m.index === regex_fptext.lastIndex) {
                  regex_fptext.lastIndex++;
              }
              var degrees, layer;
              if (m.length === 7) {
                  degrees = m[5];
                  layer = m[6];
              } else {
                  degrees = 0;
                  layer = m[5];
              }
              var fp_text = {
                  type: m[1],
                  text: m[2],
                  x: m[3],
                  y: m[4],
                  degrees: degrees,
                  layer: layer
              };
              update_dimensions(fp_text['x'], fp_text['y']);
              fp_texts.push(fp_text);
          }

          // check if current line is a text effect
          var regex_fptext_efx = /\(effects \(font \(size ([.\d]+) ([.\d]+)\) \(thickness ([.\d]+)\)\)\)/g;
          while ((m = regex_fptext_efx.exec(line)) !== null) {
              if (m.index === regex_fptext_efx.lastIndex) {
                  regex_fptext_efx.lastIndex++;
              }
              fp_texts[fp_texts.length - 1]['width'] = m[1];
              fp_texts[fp_texts.length - 1]['height'] = m[2];
              fp_texts[fp_texts.length - 1]['thickness'] = m[3];
          }
      }

      // debugging
      console.log("DEBUG: found " + fp_lines.length + " fp_lines");
      console.log("DEBUG: found " + fp_circles.length + " fp_circles");
      console.log("DEBUG: found " + fp_arcs.length + " fp_arcs");
      console.log("DEBUG: found " + fp_texts.length + " fp_texts");
      console.log("DEBUG: found " + pads.length + " pads");

      // calculate zoom factor
      var canvas_width = canvas.width / 2;
      var canvas_height = canvas.height / 2;
      var max_width = Math.max(Math.abs(left), Math.abs(right));
      var max_height = Math.max(Math.abs(top), Math.abs(bottom));
      if (!zoom) {
          zoom = Math.min((canvas_width - 10) / max_width, (canvas_height - 10) / max_height);
          default_zoom = zoom;
      }

      // more debugging
      console.log("DEBUG: max dimensions: left=" + left + "; right=" + right + "; top=" + top + "; bottom=" + bottom);
      console.log("DEBUG: zoom: " + zoom);
      console.log("DEBUG: moved: " + move_x + "x" + move_y);

      // draw everything
      draw_grid(options['grid'] * zoom);

      var j;
      for (j = 0; j < fp_lines.length; j++) {
          var fpline = fp_lines[j];
          // translate coords
          fpline['x1'] = fpline['x1'] * zoom + canvas_width + move_x;
          fpline['y1'] = fpline['y1'] * zoom + canvas_height + move_y;
          fpline['x2'] = fpline['x2'] * zoom + canvas_width + move_x;
          fpline['y2'] = fpline['y2'] * zoom + canvas_height + move_y;
          fpline['width'] *= zoom;

          draw_fpline(fpline);
      }

      for (j = 0; j < fp_circles.length; j++) {
          var fpcircle = fp_circles[j];
          // translate coords
          fpcircle['center_x'] = fpcircle['center_x'] * zoom + canvas_width + move_x;
          fpcircle['center_y'] = fpcircle['center_y'] * zoom + canvas_height + move_y;
          fpcircle['radius'] *= zoom;
          fpcircle['width'] *= zoom;

          draw_fpcircle(fpcircle);
      }

      for (j = 0; j < fp_arcs.length; j++) {
          var fparc = fp_arcs[j];
          // translate coords
          fparc['center_x'] = fparc['center_x'] * zoom + canvas_width + move_x;
          fparc['center_y'] = fparc['center_y'] * zoom + canvas_height + move_y;
          fparc['point_x'] = fparc['point_x'] * zoom + canvas_width + move_x;
          fparc['point_y'] = fparc['point_y'] * zoom + canvas_height + move_y;
          fparc['width'] *= zoom;
          fparc['radius'] *= zoom;

          draw_fparc(fparc);
      }

      for (j = 0; j < fp_texts.length; j++) {
          let fptext = fp_texts[j];
          draw_fptext(fptext);
      }

      for (j = 0; j < pads.length; j++) {
          pad = pads[j];
          // translate coords
          pad['x'] = pad['x'] * zoom + canvas_width + move_x;
          pad['y'] = pad['y'] * zoom + canvas_height + move_y;
          pad['width'] *= zoom;
          pad['height'] *= zoom;
          pad['drill'] *= zoom;

          draw_pad(pad);
      }
  };

  this.render = function(footprint) {
      data = footprint;
      return draw_footprint();
  };

  this.zoom = function(level) {
      zoom = zoom + level;
      return draw_footprint();
  };

  this.move_up = function(px) {
      move_y = move_y + px;
      return draw_footprint();
  };

  this.move_down = function(px) {
      move_y = move_y - px;
      return draw_footprint();
  };

  this.move_left = function(px) {
      move_x = move_x + px;
      return draw_footprint();
  };

  this.move_right = function(px) {
      move_x = move_x - px;
      return draw_footprint();
  };

  this.reset = function() {
      zoom = default_zoom;
      move_x = 0;
      move_y = 0;
      return draw_footprint();
  };

  canvas.addEventListener('scroll', function(event) {
      return console.log(event);
  });

  return this;
};
