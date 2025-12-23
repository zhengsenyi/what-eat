// pages/profile/profile.js
const { userApi, BASE_URL } = require('../../utils/api');

// 处理头像URL，如果是相对路径则拼接服务器地址
function getFullAvatarUrl(avatarUrl) {
  if (!avatarUrl) return '';
  if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://') || avatarUrl.startsWith('wxfile://')) {
    return avatarUrl;
  }
  // 相对路径，拼接服务器地址
  return BASE_URL + avatarUrl;
}

Page({
  data: {
    // 导航栏相关
    statusBarHeight: 20,
    navBarHeight: 44,
    menuButtonWidth: 87,
    // 用户信息
    userInfo: {
      id: 0,
      username: '',
      nickName: '美食探索家',
      avatarText: '👤',
      avatarUrl: '', // 微信头像URL
      level: '黄金会员',
      remainingTimes: 3,
      isWechatUser: false
    },
    version: '1.0.0',
    cacheSize: '计算中...',
    // 编辑用户信息弹窗
    showEditModal: false,
    tempAvatarUrl: '',
    tempNickname: ''
  },

  onLoad() {
    // 获取导航栏信息
    this.getNavBarInfo();
    this.loadUserInfo();
    this.calculateCacheSize();
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.loadUserInfo();
    this.calculateCacheSize();
  },

  // 获取导航栏信息
  getNavBarInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
      const navBarHeight = (menuButtonInfo.top - statusBarHeight) * 2 + menuButtonInfo.height;
      const menuButtonWidth = systemInfo.windowWidth - menuButtonInfo.left;
      
      this.setData({
        statusBarHeight,
        navBarHeight,
        menuButtonWidth
      });
    } catch (e) {
      console.error('获取导航栏信息失败', e);
    }
  },

  // 加载用户信息
  async loadUserInfo() {
    try {
      const res = await userApi.getUserInfo();
      
      // 后端返回格式：{code: 0, data: {id, username, nickname, avatar_url, openid, created_at, today_remaining_times}}
      if (res && res.code === 0 && res.data) {
        const userInfo = res.data;
        const localUserInfo = wx.getStorageSync('userInfo') || {};
        
        // 优先使用后端返回的昵称和头像
        const nickName = userInfo.nickname || localUserInfo.nickName || userInfo.username || '美食探索家';
        const rawAvatarUrl = userInfo.avatar_url || localUserInfo.avatarUrl || '';
        const avatarUrl = getFullAvatarUrl(rawAvatarUrl);
        const isWechatUser = !!userInfo.openid;
        
        this.setData({
          userInfo: {
            id: userInfo.id,
            username: userInfo.username,
            nickName: nickName,
            avatarText: localUserInfo.avatarText || '👤',
            avatarUrl: avatarUrl,
            level: '黄金会员',
            remainingTimes: userInfo.today_remaining_times,
            isWechatUser: isWechatUser
          }
        });

        // 更新本地存储（存储原始URL）
        wx.setStorageSync('userInfo', {
          ...localUserInfo,
          id: userInfo.id,
          username: userInfo.username,
          nickName: nickName,
          avatarUrl: rawAvatarUrl,
          remainingTimes: userInfo.today_remaining_times,
          isWechatUser: isWechatUser
        });
      }
    } catch (e) {
      console.error('获取用户信息失败', e);
      // 使用本地存储的信息
      const localUserInfo = wx.getStorageSync('userInfo');
      if (localUserInfo) {
        this.setData({
          userInfo: {
            id: localUserInfo.id || 0,
            username: localUserInfo.username || '',
            nickName: localUserInfo.nickName || '美食探索家',
            avatarText: localUserInfo.avatarText || '👤',
            avatarUrl: getFullAvatarUrl(localUserInfo.avatarUrl || ''),
            level: '黄金会员',
            remainingTimes: localUserInfo.remainingTimes || 0,
            isWechatUser: localUserInfo.isWechatUser || false
          }
        });
      }
    }
  },

  // 计算缓存大小
  calculateCacheSize() {
    try {
      const res = wx.getStorageInfoSync();
      const usedSize = res.currentSize;
      let sizeText = '';
      
      if (usedSize < 1024) {
        sizeText = `${usedSize} KB`;
      } else {
        sizeText = `${(usedSize / 1024).toFixed(2)} MB`;
      }
      
      this.setData({ cacheSize: sizeText });
    } catch (e) {
      this.setData({ cacheSize: '未知' });
    }
  },

  // 编辑个人资料
  editProfile() {
    const { userInfo } = this.data;
    // 如果是微信用户，显示编辑弹窗
    if (userInfo.isWechatUser) {
      // 获取当前头像URL用于编辑弹窗显示
      const currentAvatarUrl = userInfo.avatarUrl || '';
      this.setData({
        showEditModal: true,
        tempAvatarUrl: currentAvatarUrl,
        tempNickname: userInfo.nickName || ''
      });
    } else {
      // 非微信用户使用原来的方式
      wx.showActionSheet({
        itemList: ['修改昵称', '修改头像'],
        success: (res) => {
          if (res.tapIndex === 0) {
            this.editNickname();
          } else if (res.tapIndex === 1) {
            this.editAvatar();
          }
        }
      });
    }
  },

  // 选择头像回调（微信用户）
  async onChooseAvatar(e) {
    const { avatarUrl } = e.detail;
    console.log('选择的头像临时路径:', avatarUrl);
    
    // 先显示临时头像
    this.setData({
      tempAvatarUrl: avatarUrl
    });

    // 上传头像到服务器
    wx.showLoading({ title: '上传中...', mask: true });
    try {
      const res = await userApi.uploadAvatar(avatarUrl);
      console.log('头像上传响应:', res);
      
      if (res && res.code === 0 && res.data && res.data.avatar_url) {
        // 使用服务器返回的URL
        const serverAvatarUrl = res.data.avatar_url;
        this.setData({
          tempAvatarUrl: serverAvatarUrl
        });
        console.log('头像上传成功，服务器URL:', serverAvatarUrl);
      } else {
        console.error('头像上传失败:', res);
        wx.showToast({
          title: res?.msg || '头像上传失败',
          icon: 'none'
        });
      }
    } catch (err) {
      console.error('头像上传异常:', err);
      wx.showToast({
        title: '头像上传失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  },

  // 输入昵称回调（微信用户）
  onNicknameInput(e) {
    const nickname = e.detail.value;
    console.log('输入的昵称:', nickname);
    this.setData({
      tempNickname: nickname
    });
  },

  // 确认修改用户信息（微信用户）
  async onConfirmEdit() {
    const { tempAvatarUrl, tempNickname, userInfo } = this.data;
    
    // 检查是否有修改
    const hasAvatarChange = tempAvatarUrl && tempAvatarUrl !== userInfo.avatarUrl;
    const hasNicknameChange = tempNickname && tempNickname !== userInfo.nickName;
    
    if (!hasAvatarChange && !hasNicknameChange) {
      this.setData({ showEditModal: false });
      return;
    }

    wx.showLoading({ title: '保存中...', mask: true });

    try {
      let finalAvatarUrl = tempAvatarUrl;
      
      // 如果头像是临时文件路径，需要先上传
      if (hasAvatarChange && tempAvatarUrl && (tempAvatarUrl.startsWith('http://tmp') || tempAvatarUrl.startsWith('wxfile://'))) {
        console.log('检测到临时头像路径，开始上传...');
        const uploadRes = await userApi.uploadAvatar(tempAvatarUrl);
        if (uploadRes && uploadRes.code === 0 && uploadRes.data && uploadRes.data.avatar_url) {
          finalAvatarUrl = uploadRes.data.avatar_url;
          console.log('头像上传成功:', finalAvatarUrl);
        } else {
          throw new Error(uploadRes?.msg || '头像上传失败');
        }
      }

      // 如果只有昵称修改，调用更新接口
      if (hasNicknameChange) {
        const res = await userApi.updateWechatUserInfo(tempNickname, null);
        console.log('更新昵称响应:', res);
        if (res && res.code !== 0) {
          throw new Error(res?.msg || '保存昵称失败');
        }
      }

      // 更新本地数据
      const newUserInfo = { ...userInfo };
      if (hasNicknameChange) {
        newUserInfo.nickName = tempNickname;
      }
      if (hasAvatarChange) {
        // 显示时使用完整URL
        newUserInfo.avatarUrl = getFullAvatarUrl(finalAvatarUrl);
      }
      
      this.setData({
        userInfo: newUserInfo,
        showEditModal: false
      });

      // 更新本地存储（存储原始URL）
      const localUserInfo = wx.getStorageSync('userInfo') || {};
      if (hasNicknameChange) {
        localUserInfo.nickName = tempNickname;
      }
      if (hasAvatarChange) {
        localUserInfo.avatarUrl = finalAvatarUrl;
      }
      wx.setStorageSync('userInfo', localUserInfo);

      wx.hideLoading();
      wx.showToast({
        title: '修改成功',
        icon: 'success'
      });
    } catch (err) {
      wx.hideLoading();
      console.error('更新用户信息失败', err);
      wx.showToast({
        title: err.message || '保存失败，请稍后重试',
        icon: 'none'
      });
    }
  },

  // 取消编辑
  onCancelEdit() {
    this.setData({ showEditModal: false });
  },

  // 修改昵称（非微信用户）
  editNickname() {
    wx.showModal({
      title: '修改昵称',
      editable: true,
      placeholderText: '请输入新昵称',
      success: (res) => {
        if (res.confirm && res.content) {
          const userInfo = wx.getStorageSync('userInfo') || {};
          userInfo.nickName = res.content;
          wx.setStorageSync('userInfo', userInfo);
          
          this.setData({
            'userInfo.nickName': res.content
          });
          
          wx.showToast({
            title: '修改成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 修改头像（非微信用户）
  editAvatar() {
    const avatars = ['👤', '😊', '🤗', '😎', '🥳', '🤩', '😋', '🍜'];
    wx.showActionSheet({
      itemList: avatars,
      success: (res) => {
        const userInfo = wx.getStorageSync('userInfo') || {};
        userInfo.avatarText = avatars[res.tapIndex];
        wx.setStorageSync('userInfo', userInfo);
        
        this.setData({
          'userInfo.avatarText': avatars[res.tapIndex]
        });
        
        wx.showToast({
          title: '修改成功',
          icon: 'success'
        });
      }
    });
  },

  // 跳转到历史页
  goToHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    });
  },

  // 跳转到意见反馈
  goToFeedback() {
    wx.showModal({
      title: '意见反馈',
      content: '如有问题或建议，请联系我们：\nfeedback@chisha.com',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 跳转到关于我们
  goToAbout() {
    wx.showModal({
      title: '关于选餐侠',
      content: '版本：1.0.0\n\n选餐侠是一款帮助你解决"今天吃什么"难题的小程序。\n\n让美食选择变得有趣又简单！',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 清除缓存
  clearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定要清除所有缓存数据吗？这将清除本地历史记录，但不会影响登录状态。',
      confirmText: '确定清除',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          const token = wx.getStorageSync('token');
          const userInfo = wx.getStorageSync('userInfo');
          
          wx.clearStorageSync();
          
          if (token) {
            wx.setStorageSync('token', token);
          }
          if (userInfo) {
            wx.setStorageSync('userInfo', userInfo);
          }
          
          this.calculateCacheSize();
          
          wx.showToast({
            title: '清除成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      confirmText: '退出',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          
          wx.showToast({
            title: '已退出登录',
            icon: 'none',
            duration: 1500
          });
          
          setTimeout(() => {
            wx.reLaunch({
              url: '/pages/login/login'
            });
          }, 1500);
        }
      }
    });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '选餐侠 - 解决你的选择困难症！',
      path: '/pages/login/login'
    };
  }
});
