// 你可以写 TypeScript, 这会帮你很大忙! 它会在你按 F5 时自动生成 JavaScript 到 build 文件夹中
// 你当然也可以直接写 JavaScript, 但是如果遇到本来很直接的错误... 慢慢折腾吧
function detectMessageUpdated(message_id: number) {
  alert(`你刚刚修改了第 ${message_id} 条聊天消息对吧😡`);
}
eventOn(tavern_events.MESSAGE_UPDATED, detectMessageUpdated);