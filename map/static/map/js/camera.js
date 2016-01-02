/*
 * A Camera object that can be used to maintain a viewport container.
 */
var Camera = function() {
    this.x = Number.MAX_SAFE_INTEGER;
    this.y = Number.MAX_SAFE_INTEGER;
    this.width = 0;
    this.height = 0;
    this.scale = 1.0
};
Camera.prototype.include = function(x, y) {
    if (x < this.x) this.x = x;
    else if (x - this.x > this.width) this.width = x - this.x;
    if (y < this.y) this.y = y;
    else if (y - this.y > this.height) this.height = y - this.y;
};
Camera.prototype.init = function(width, height) {
    scaleX = width / this.width;
    scaleY = height / this.height;
    this.scale = Math.min(scaleX, scaleY);
};
Camera.prototype.apply = function(viewport) {
    viewport.scale.x = this.scale;
    viewport.scale.y = this.scale;

    viewport.position.x = -(this.x - 10) * this.scale;
    viewport.position.y = -(this.y - 10) * this.scale;
};