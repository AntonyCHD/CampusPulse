"""
事件类型分类器

基于内容的校园话题分类（7类 + 兜底）
"""


class EventTypeClassifier:
    """内容关键词事件类型分类器"""

    RULES = {
        "食堂餐饮": [
            "食堂", "餐厅", "饭菜", "麻辣烫", "麻辣香锅", "小笼包", "摊位",
            "外卖", "涨价", "伙食", "菜品", "早餐", "午餐", "晚餐", "夜宵",
            "味道", "难吃", "好吃", "分量", "窗口", "打饭", "食物",
            "奶茶", "咖啡", "水果", "超市", "便利店", "小吃",
        ],
        "宿舍生活": [
            "宿舍", "寝室", "女寝", "男寝", "中蓝", "梆子井", "住宿",
            "水电", "停电", "停水", "空调", "暖气", "限电", "断电",
            "洗澡", "卫生间", "洗衣机", "房间", "室友", "查寝",
            "门禁", "装修", "施工", "噪音", "凌晨",
        ],
        "学术教务": [
            "考试", "成绩", "分数", "挂科", "补考", "重修", "绩点", "GPA",
            "六级", "四级", "英语", "保研", "考研", "研究生", "博士",
            "课程", "选课", "老师", "教授", "教学", "上课", "课堂",
            "作业", "论文", "答辩", "毕业", "学分", "学号", "学籍",
            "作弊", "抄袭", "奖学金", "综测", "排名", "艺考",
        ],
        "校园管理": [
            "学校", "校方", "领导", "校长", "书记", "辅导员", "教务处",
            "学生处", "后勤", "行政", "通知", "规定", "制度", "政策",
            "认证", "管理", "处理", "解决", "回应", "投诉", "维权",
            "收费", "费用", "退费", "罚款", "举报",
        ],
        "校园安全": [
            "安全", "危险", "偷", "盗窃", "报警", "保安", "监控",
            "陌生人", "跟踪", "骚扰", "打架", "暴力", "死亡",
            "火灾", "事故", "受伤", "急救", "隐私",
        ],
        "网络舆情": [
            "热搜", "曝光", "吃瓜", "围观", "转发", "扩散", "求证",
            "造谣", "辟谣", "真相", "实际", "事实", "证据",
            "据说", "听说", "内部消息", "关系户", "黑幕",
        ],
        "社团活动": [
            "社团", "活动", "比赛", "演出", "晚会", "运动会", "篮球",
            "足球", "体育", "文艺", "学生会", "志愿者", "报名",
            "参加", "举办", "组织", "记录", "校队",
        ],
    }

    def classify(self, text: str) -> str:
        """对单条文本进行事件类型分类"""
        scores = {}
        text_lower = text.lower()
        for category, keywords in self.RULES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        if not scores:
            return "综合讨论"
        return max(scores, key=scores.get)

    def classify_event(self, event: dict) -> str:
        """对事件（含post+comments）进行分类"""
        text = event.get("post", {}).get("text", "")
        for c in event.get("comments", []):
            text += " " + c.get("text", "")
        return self.classify(text)


# Singleton
_classifier: EventTypeClassifier | None = None


def get_classifier() -> EventTypeClassifier:
    global _classifier
    if _classifier is None:
        _classifier = EventTypeClassifier()
    return _classifier
