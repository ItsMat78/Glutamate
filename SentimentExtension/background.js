chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "analyzeSentiment",
      title: "Analyze Sentiment",
      contexts: ["selection"]
    });
  });
  
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "analyzeSentiment") {
      chrome.storage.local.set({ selectedText: info.selectionText }, () => {
        chrome.action.openPopup();
      });
    }
  });
  