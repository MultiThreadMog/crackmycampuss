from driver_logic import cars, pygame
import driver_logic
import time

# tracking displayed data
start_time = time.time()
last_throughput_update = time.time()
cars_per_minute = 0
recent_cars_passed = 0

def draw_stats(screen, signal_stats):
    global last_throughput_update, cars_per_minute, recent_cars_passed
    
    font = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 22)
    y_offset = 10
    
    # calculate data
    current_time = time.time()
    elapsed = current_time - start_time
    
    # Update every second
    if current_time - last_throughput_update >= 1.0:
        cars_per_minute = int((driver_logic.cars_passed / elapsed) * 60) if elapsed > 0 else 0
        last_throughput_update = current_time
    
    # Cars passed
    text = font.render(f"Cars Passed: {driver_logic.cars_passed}", True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += 30
    
    # Throughput
    text = font.render(f"Throughput: {cars_per_minute} cars/min", True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += 30
    
    # Active cars
    text = font.render(f"Active Cars: {len(cars)}", True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += 40
    
    # traffic light cycles
    text = font.render("Traffic Light Cycles:", True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += 25
    
    # Lane stats
    from signal_control import vehicle_counts
    for lane in ["bottom", "right", "top", "left"]:
        count = signal_stats.get(lane, 0)
        waiting = vehicle_counts.get(lane, 0)
        
        # waiting vehicles text color
        if waiting > 5:
            color = (255, 100, 100)  
        elif waiting > 2:
            color = (255, 200, 100) 
        else:
            color = (200, 200, 200)
        
        text = font_small.render(f"  {lane}: {count} cycles | {waiting} waiting", True, color)
        screen.blit(text, (10, y_offset))
        y_offset += 25
    
    # Runtime
    runtime_mins = int(elapsed / 60)
    runtime_secs = int(elapsed % 60)
    text = font_small.render(f"Runtime: {runtime_mins}m {runtime_secs}s", True, (180, 180, 180))
    screen.blit(text, (10, y_offset))