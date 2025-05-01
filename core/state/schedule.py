from typing import List, Dict, Optional
import random
from datetime import datetime, timedelta
from utils.helpers import current_timestamp

class ScheduleSystem:
    def __init__(self):
        self.schedule: List[Dict] = []
        self.last_update = current_timestamp()
    
    def generate_daily_schedule(self):
        """生成每日日程"""
        self.schedule = []
        now = datetime.now()
        
        # 基础活动类型
        activities = ['creative', 'analytical', 'social', 'routine', 'rest']
        weights = [0.2, 0.3, 0.2, 0.2, 0.1]  # 活动权重
        
        # 生成一天的日程 (8个时间段)
        for i in range(8):
            start_time = now + timedelta(hours=i*3)
            end_time = start_time + timedelta(hours=3)
            
            activity = random.choices(activities, weights=weights)[0]
            
            self.schedule.append({
                'start': start_time.timestamp(),
                'end': end_time.timestamp(),
                'activity': activity,
                'completed': False
            })
    
    def get_current_activity(self) -> Optional[Dict]:
        """获取当前活动"""
        now = current_timestamp()
        for activity in self.schedule:
            if activity['start'] <= now <= activity['end'] and not activity['completed']:
                return activity
        return None
    
    def complete_activity(self, activity_id: int):
        """标记活动为完成"""
        if 0 <= activity_id < len(self.schedule):
            self.schedule[activity_id]['completed'] = True
    
    def get_upcoming_activities(self, count: int = 3) -> List[Dict]:
        """获取即将到来的活动"""
        now = current_timestamp()
        upcoming = [a for a in self.schedule if a['start'] > now]
        return sorted(upcoming, key=lambda x: x['start'])[:count]
    
    def update(self):
        """更新日程系统"""
        # 每天更新一次日程
        if current_timestamp() - self.last_update > 86400:
            self.generate_daily_schedule()
            self.last_update = current_timestamp()