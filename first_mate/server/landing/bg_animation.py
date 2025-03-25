import pyhtml as p

def generate_bg_animation() -> p.script:
    return p.script("""
            // Friendship-themed background animation
            document.addEventListener('DOMContentLoaded', function() {
              const canvas = document.getElementById('animation-canvas');
              const ctx = canvas.getContext('2d');
              
              // Set canvas size to match window
              function resizeCanvas() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
              }
              
              resizeCanvas();
              window.addEventListener('resize', resizeCanvas);
              
              // Mouse position for interactive effects
              let mouse = {
                x: null,
                y: null,
                radius: 120
              };
              
              window.addEventListener('mousemove', function(event) {
                mouse.x = event.x;
                mouse.y = event.y;
              });
              
              // Colors for people/connection nodes
              const colorPalette = [
                '#fca33b', // Main brand color
                '#f55e40', // Red 
                '#6991bd', // Blue
                '#ddcfbe', // Beige
                '#d1e231'  // Green
              ];
              
              // Person class - represents a person/student
              class Person {
                constructor(x, y) {
                  this.x = x || Math.random() * canvas.width;
                  this.y = y || Math.random() * canvas.height;
                  this.size = Math.random() * 3 + 3; // Person node size
                  this.baseSize = this.size;
                  this.speedX = Math.random() * 1 - 0.5;
                  this.speedY = Math.random() * 1 - 0.5;
                  this.colorIndex = Math.floor(Math.random() * colorPalette.length);
                  this.color = colorPalette[this.colorIndex];
                  this.connections = []; // Other people this person is connected to
                  this.connectionStrength = {}; // Strength of each connection
                  this.isSearching = Math.random() > 0.7; // Some people are actively searching for friends
                  this.searchRadius = Math.random() * 100 + 50;
                  this.friendshipLevel = 0; // Starts with no friends
                  this.pulseSpeed = 0.01 + Math.random() * 0.02;
                  this.pulseDirection = 1;
                  this.pulseAmount = 0;
                }
                
                update(people) {
                  // Move people around
                  this.x += this.speedX;
                  this.y += this.speedY;
                  
                  // Bounce off edges
                  if (this.x > canvas.width || this.x < 0) {
                    this.speedX = -this.speedX;
                  }
                  if (this.y > canvas.height || this.y < 0) {
                    this.speedY = -this.speedY;
                  }
                  
                  // Pulse effect
                  this.pulseAmount += this.pulseSpeed * this.pulseDirection;
                  if (this.pulseAmount > 1 || this.pulseAmount < 0) {
                    this.pulseDirection *= -1;
                  }
                  
                  // People searching for friends move more actively
                  if (this.isSearching) {
                    this.speedX += (Math.random() * 0.4 - 0.2);
                    this.speedY += (Math.random() * 0.4 - 0.2);
                    
                    // Limit speed
                    const maxSpeed = 1.5;
                    const currentSpeed = Math.sqrt(this.speedX * this.speedX + this.speedY * this.speedY);
                    if (currentSpeed > maxSpeed) {
                      this.speedX = (this.speedX / currentSpeed) * maxSpeed;
                      this.speedY = (this.speedY / currentSpeed) * maxSpeed;
                    }
                  }
                  
                  // Find and build connections with nearby people
                  this.connections = [];
                  for (let i = 0; i < people.length; i++) {
                    if (people[i] === this) continue;
                    
                    const dx = this.x - people[i].x;
                    const dy = this.y - people[i].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    // If people are close enough, they can connect
                    if (distance < this.searchRadius) {
                      this.connections.push(people[i]);
                      
                      // Build friendship over time when close
                      if (!this.connectionStrength[i]) {
                        this.connectionStrength[i] = 0.1; // Initial connection
                      } else if (this.connectionStrength[i] < 1) {
                        this.connectionStrength[i] += 0.001; // Friendship grows slowly
                      }
                      
                      // People who are friends tend to move together
                      if (this.connectionStrength[i] > 0.5) {
                        this.speedX += dx * 0.0001;
                        this.speedY += dy * 0.0001;
                      }
                    } else {
                      // Connections fade when people move apart
                      if (this.connectionStrength[i]) {
                        this.connectionStrength[i] -= 0.0005;
                        if (this.connectionStrength[i] <= 0) {
                          delete this.connectionStrength[i];
                        }
                      }
                    }
                  }
                  
                  // Update friendship level based on connections
                  this.friendshipLevel = Object.values(this.connectionStrength).reduce((sum, val) => sum + val, 0);
                  
                  // Interactive effect with mouse - represents user helping make connections
                  if (mouse.x != null && mouse.y != null) {
                    const dx = mouse.x - this.x;
                    const dy = mouse.y - this.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < mouse.radius) {
                      // Mouse helps people find each other
                      const forceDirectionX = dx / distance;
                      const forceDirectionY = dy / distance;
                      const force = (mouse.radius - distance) / mouse.radius;
                      
                      // Move toward mouse
                      this.speedX += forceDirectionX * force * 0.2;
                      this.speedY += forceDirectionY * force * 0.2;
                      
                      // Temporarily increase search radius when near mouse
                      this.searchRadius = this.searchRadius * 1.5;
                      
                      // Highlight person when near mouse
                      this.size = this.baseSize + (mouse.radius - distance) / 20;
                    } else {
                      // Return to normal
                      this.searchRadius = Math.random() * 100 + 50;
                      if (this.size > this.baseSize) {
                        this.size -= 0.1;
                      }
                    }
                  }
                  
                  // Add friction to gradually slow people
                  this.speedX *= 0.98;
                  this.speedY *= 0.98;
                }
                
                draw() {
                  // Draw person node
                  ctx.beginPath();
                  ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                  
                  // People with more friends appear brighter
                  const brightness = 0.5 + Math.min(this.friendshipLevel, 1) * 0.5;
                  
                  // Create gradient for person
                  const gradient = ctx.createRadialGradient(
                    this.x, this.y, 0,
                    this.x, this.y, this.size * 2
                  );
                  
                  gradient.addColorStop(0, this.color);
                  gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                  
                  ctx.fillStyle = gradient;
                  ctx.globalAlpha = brightness * (0.7 + this.pulseAmount * 0.3);
                  ctx.fill();
                  
                  // People searching for friends have a subtle pulsing outline
                  if (this.isSearching) {
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size + 2 + Math.sin(Date.now() * 0.005) * 2, 0, Math.PI * 2);
                    ctx.strokeStyle = this.color;
                    ctx.globalAlpha = 0.3;
                    ctx.stroke();
                  }
                  
                  // Draw friendship connections
                  for (let i = 0; i < this.connections.length; i++) {
                    const friend = this.connections[i];
                    const index = people.indexOf(friend);
                    const strength = this.connectionStrength[index] || 0;
                    
                    if (strength > 0.1) { // Only show meaningful connections
                      // Create gradient line between people
                      const gradient = ctx.createLinearGradient(
                        this.x, this.y,
                        friend.x, friend.y
                      );
                      
                      gradient.addColorStop(0, this.color);
                      gradient.addColorStop(1, friend.color);
                      
                      ctx.strokeStyle = gradient;
                      ctx.lineWidth = strength * 2; // Stronger friendships have thicker lines
                      ctx.globalAlpha = strength * 0.8;
                      ctx.beginPath();
                      ctx.moveTo(this.x, this.y);
                      ctx.lineTo(friend.x, friend.y);
                      ctx.stroke();
                      
                      // Draw small heart or friendship symbol on strong connections
                      if (strength > 0.7) {
                        const midX = (this.x + friend.x) / 2;
                        const midY = (this.y + friend.y) / 2;
                        
                        // Draw heart
                        const heartSize = strength * 4;
                        ctx.fillStyle = '#f55e40';
                        ctx.globalAlpha = strength * 0.9;
                        
                        // Simple heart shape
                        ctx.beginPath();
                        ctx.moveTo(midX, midY + heartSize * 0.3);
                        ctx.bezierCurveTo(
                          midX, midY, 
                          midX - heartSize, midY - heartSize, 
                          midX, midY - heartSize * 0.5
                        );
                        ctx.bezierCurveTo(
                          midX + heartSize, midY - heartSize, 
                          midX, midY, 
                          midX, midY + heartSize * 0.3
                        );
                        ctx.fill();
                      }
                    }
                  }
                }
              }
              
              // Create people
              const peopleCount = Math.min(40, Math.floor(window.innerWidth * window.innerHeight / 20000));
              const people = [];
              
              for (let i = 0; i < peopleCount; i++) {
                people.push(new Person());
              }
              
              // Occasionally add new people to the campus
              function addNewPerson() {
                if (people.length < 60 && Math.random() < 0.1) {
                  // New people enter from the edges
                  let x, y;
                  if (Math.random() > 0.5) {
                    x = Math.random() > 0.5 ? 0 : canvas.width;
                    y = Math.random() * canvas.height;
                  } else {
                    x = Math.random() * canvas.width;
                    y = Math.random() > 0.5 ? 0 : canvas.height;
                  }
                  
                  people.push(new Person(x, y));
                }
                
                setTimeout(addNewPerson, 3000);
              }
              
              addNewPerson();
              
              // Animation loop
              let animationFrameId;
              
              function animate() {
                animationFrameId = requestAnimationFrame(animate);
                
                // Clear canvas with slight transparency for trail effect
                ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Update and draw people and their connections
                for (let i = 0; i < people.length; i++) {
                  people[i].update(people);
                }
                
                // Draw all people after updating positions
                for (let i = 0; i < people.length; i++) {
                  people[i].draw();
                }
                
                // Occasionally create "friendship events" where people come together
                if (Math.random() < 0.001) {
                  createFriendshipEvent();
                }
              }
              
              // Create a friendship event - a group of people coming together
              function createFriendshipEvent() {
                const eventX = Math.random() * canvas.width;
                const eventY = Math.random() * canvas.height;
                const eventRadius = Math.random() * 100 + 50;
                
                // Select random people to participate
                const participants = [];
                for (let i = 0; i < people.length; i++) {
                  if (Math.random() < 0.3) {
                    participants.push(people[i]);
                    
                    // Move them toward the event
                    const dx = eventX - people[i].x;
                    const dy = eventY - people[i].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    people[i].speedX += (dx / distance) * 0.5;
                    people[i].speedY += (dy / distance) * 0.5;
                    
                    // Make them search for friends
                    people[i].isSearching = true;
                    people[i].searchRadius = eventRadius;
                  }
                }
              }
              
              animate();
              
              // Clean up animation on page unload
              window.addEventListener('beforeunload', function() {
                cancelAnimationFrame(animationFrameId);
              });
              
              // Logo animation
              const logo = document.querySelector('.logo-icon-small');
              if (logo) {
                logo.addEventListener('mouseover', function() {
                  this.style.transition = 'transform 0.5s ease';
                  this.style.transform = 'rotate(20deg) scale(1.2)';
                });
                
                logo.addEventListener('mouseout', function() {
                  this.style.transition = 'transform 0.5s ease';
                  this.style.transform = 'rotate(0deg) scale(1)';
                });
                
                // Add subtle pulse animation
                function pulseLogo() {
                  logo.style.transition = 'transform 1.5s ease-in-out';
                  logo.style.transform = 'scale(1.05)';
                  
                  setTimeout(() => {
                    logo.style.transform = 'scale(1)';
                  }, 1500);
                  
                  setTimeout(pulseLogo, 3000);
                }
                
                pulseLogo();
              }
            });
        """)