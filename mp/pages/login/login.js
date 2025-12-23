// pages/login/login.js
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
    isLoading: false,
    isWechatLoading: false,
    isRegisterMode: false,
    username: '',
    password: '',
    confirmPassword: '',
    // 新用户信息填写弹窗
    showUserInfoModal: false,
    tempAvatarUrl: '',
    tempNickname: '',
    // 临时保存的用户数据
    pendingUserData: null
  },

  onLoad() {
    // 检查是否已登录
    const token = wx.getStorageSync('token');
    console.log('检查登录状态，token:', token ? '存在' : '不存在');
    if (token) {
      console.log('已登录，跳转到首页');
      wx.reLaunch({
        url: '/pages/index/index',
        success: () => {
          console.log('自动跳转成功');
        },
        fail: (err) => {
          console.error('自动跳转失败:', err);
        }
      });
    }
  },

  // 切换登录/注册模式
  toggleMode() {
    this.setData({
      isRegisterMode: !this.data.isRegisterMode,
      username: '',
      password: '',
      confirmPassword: ''
    });
  },

  // 输入用户名
  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  // 输入密码
  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  // 输入确认密码
  onConfirmPasswordInput(e) {
    this.setData({ confirmPassword: e.detail.value });
  },

  // 登录
  async onLogin() {
    if (this.data.isLoading) return;

    const { username, password } = this.data;

    // 验证输入
    if (!username || username.length < 3) {
      wx.showToast({ title: '用户名至少3个字符', icon: 'none' });
      return;
    }
    if (!password || password.length < 6) {
      wx.showToast({ title: '密码至少6个字符', icon: 'none' });
      return;
    }

    this.setData({ isLoading: true });
    wx.showLoading({ title: '登录中...', mask: true });

    try {
      console.log('开始登录请求...');
      const res = await userApi.login(username, password);
      console.log('登录响应:', res);
      
      // 检查响应格式：后端返回 {code: 0, msg: "登录成功", data: {access_token: "..."}}
      if (!res || res.code !== 0 || !res.data || !res.data.access_token) {
        throw new Error(res?.msg || '登录响应无效');
      }
      
      // 保存token
      wx.setStorageSync('token', res.data.access_token);
      console.log('Token已保存:', res.data.access_token);
      
      // 获取用户信息
      try {
        const userInfoRes = await userApi.getUserInfo();
        console.log('用户信息响应:', userInfoRes);
        if (userInfoRes && userInfoRes.code === 0 && userInfoRes.data) {
          const userInfo = userInfoRes.data;
          wx.setStorageSync('userInfo', {
            id: userInfo.id,
            username: userInfo.username,
            nickName: userInfo.username,
            avatarText: '👤',
            level: '黄金会员',
            remainingTimes: userInfo.today_remaining_times,
            createdAt: userInfo.created_at
          });
        }
      } catch (e) {
        console.error('获取用户信息失败', e);
      }

      wx.hideLoading();
      this.setData({ isLoading: false });
      
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1000
      });

      // 跳转到首页
      this.navigateToIndex();

    } catch (err) {
      wx.hideLoading();
      this.setData({ isLoading: false });
      console.error('登录失败', err);
      
      let errorMsg = '登录失败，请检查用户名和密码';
      if (err && err.detail) {
        errorMsg = err.detail;
      } else if (err && err.message) {
        errorMsg = err.message;
      }
      
      wx.showToast({
        title: errorMsg,
        icon: 'none'
      });
    }
  },

  // 注册
  async onRegister() {
    if (this.data.isLoading) return;

    const { username, password, confirmPassword } = this.data;

    // 验证输入
    if (!username || username.length < 3) {
      wx.showToast({ title: '用户名至少3个字符', icon: 'none' });
      return;
    }
    if (!password || password.length < 6) {
      wx.showToast({ title: '密码至少6个字符', icon: 'none' });
      return;
    }
    if (password !== confirmPassword) {
      wx.showToast({ title: '两次密码输入不一致', icon: 'none' });
      return;
    }

    this.setData({ isLoading: true });
    wx.showLoading({ title: '注册中...', mask: true });

    try {
      console.log('开始注册请求...');
      await userApi.register(username, password);
      console.log('注册成功');
      
      wx.hideLoading();
      this.setData({ isLoading: false });
      
      wx.showToast({ title: '注册成功，请登录', icon: 'success', duration: 1500 });

      setTimeout(() => {
        this.setData({
          isRegisterMode: false,
          confirmPassword: ''
        });
      }, 1500);

    } catch (err) {
      wx.hideLoading();
      this.setData({ isLoading: false });
      console.error('注册失败', err);
      
      let errorMsg = '注册失败，用户名可能已存在';
      if (err && err.detail) {
        errorMsg = err.detail;
      } else if (err && err.message) {
        errorMsg = err.message;
      }
      
      wx.showToast({
        title: errorMsg,
        icon: 'none'
      });
    }
  },

  // 微信授权登录
  async onWechatLogin() {
    if (this.data.isWechatLoading) return;

    this.setData({ isWechatLoading: true });
    wx.showLoading({ title: '微信登录中...', mask: true });

    try {
      // 1. 调用 wx.login 获取 code
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        });
      });

      if (!loginRes.code) {
        throw new Error('获取微信登录凭证失败');
      }

      console.log('获取到微信code:', loginRes.code);

      // 2. 调用后端接口进行微信登录
      const res = await userApi.wechatLogin(loginRes.code);
      console.log('微信登录响应:', res);

      // 检查响应格式
      if (!res || res.code !== 0 || !res.data || !res.data.access_token) {
        throw new Error(res?.msg || '微信登录响应无效');
      }

      // 3. 保存token
      wx.setStorageSync('token', res.data.access_token);
      console.log('Token已保存:', res.data.access_token);

      const userData = res.data.user;
      const isNewUser = res.data.is_new_user;

      console.log('用户数据:', userData);
      console.log('是否新用户:', isNewUser);
      console.log('昵称:', userData.nickname, '类型:', typeof userData.nickname);
      console.log('头像:', userData.avatar_url, '类型:', typeof userData.avatar_url);

      wx.hideLoading();
      this.setData({ isWechatLoading: false });

      // 4. 如果是新用户，显示信息填写弹窗让用户完善资料
      // 注意：新用户的 nickname 和 avatar_url 通常为 null
      const needShowModal = isNewUser === true;
      console.log('是否需要显示弹窗:', needShowModal);
      
      if (needShowModal) {
        console.log('新用户，显示信息填写弹窗');
        this.setData({
          showUserInfoModal: true,
          tempAvatarUrl: '',
          tempNickname: '',
          pendingUserData: userData
        });
      } else {
        // 5. 老用户或已有信息，直接保存并跳转
        wx.setStorageSync('userInfo', {
          id: userData.id,
          openid: userData.openid,
          nickName: userData.nickname || '微信用户',
          avatarUrl: getFullAvatarUrl(userData.avatar_url) || '',
          avatarText: '👤',
          level: '黄金会员',
          isWechatUser: true,
          createdAt: userData.created_at
        });

        // 获取完整用户信息
        await this.fetchFullUserInfo();

        wx.showToast({
          title: '登录成功',
          icon: 'success',
          duration: 1000
        });

        this.navigateToIndex();
      }

    } catch (err) {
      wx.hideLoading();
      this.setData({ isWechatLoading: false });
      console.error('微信登录失败', err);

      let errorMsg = '微信登录失败，请稍后重试';
      if (err && err.msg) {
        errorMsg = err.msg;
      } else if (err && err.message) {
        errorMsg = err.message;
      }

      wx.showToast({
        title: errorMsg,
        icon: 'none'
      });
    }
  },

  // 获取完整用户信息
  async fetchFullUserInfo() {
    try {
      const userInfoRes = await userApi.getUserInfo();
      console.log('用户信息响应:', userInfoRes);
      if (userInfoRes && userInfoRes.code === 0 && userInfoRes.data) {
        const userInfo = userInfoRes.data;
        const localInfo = wx.getStorageSync('userInfo') || {};
        wx.setStorageSync('userInfo', {
          ...localInfo,
          id: userInfo.id,
          openid: userInfo.openid,
          username: userInfo.username,
          nickName: userInfo.nickname || localInfo.nickName || '微信用户',
          avatarUrl: getFullAvatarUrl(userInfo.avatar_url) || localInfo.avatarUrl || '',
          remainingTimes: userInfo.today_remaining_times,
          isWechatUser: !!userInfo.openid,
          createdAt: userInfo.created_at
        });
      }
    } catch (e) {
      console.error('获取用户信息失败', e);
    }
  },

  // 选择头像回调 - 通过 open-type="chooseAvatar" 触发（真机有效）
  async onChooseAvatar(e) {
    console.log('onChooseAvatar 被调用, e.detail:', e.detail);
    const { avatarUrl } = e.detail;
    
    if (!avatarUrl) {
      console.error('未获取到头像URL');
      return;
    }
    
    console.log('选择的头像临时路径:', avatarUrl);
    
    // 显示选择的头像
    this.setData({
      tempAvatarUrl: avatarUrl
    });
  },

  // 头像区域点击事件 - 使用 wx.chooseMedia 选择图片
  async onAvatarTap() {
    console.log('onAvatarTap 被调用');
    
    // 使用 wx.chooseMedia 选择图片
    try {
      const res = await new Promise((resolve, reject) => {
        wx.chooseMedia({
          count: 1,
          mediaType: ['image'],
          sourceType: ['album', 'camera'],
          sizeType: ['compressed'],
          success: resolve,
          fail: reject
        });
      });
      
      if (res.tempFiles && res.tempFiles.length > 0) {
        const avatarUrl = res.tempFiles[0].tempFilePath;
        console.log('选择的头像:', avatarUrl);
        
        this.setData({
          tempAvatarUrl: avatarUrl
        });
      }
    } catch (err) {
      console.error('选择图片失败:', err);
      // 用户取消不提示
      if (err.errMsg && !err.errMsg.includes('cancel')) {
        wx.showToast({
          title: '选择图片失败',
          icon: 'none'
        });
      }
    }
  },

  // 输入昵称回调
  onNicknameInput(e) {
    const nickname = e.detail.value;
    console.log('输入的昵称:', nickname);
    this.setData({
      tempNickname: nickname
    });
  },

  // 昵称输入框失去焦点
  onNicknameBlur(e) {
    const nickname = e.detail.value;
    console.log('昵称输入框失去焦点，值:', nickname);
    if (nickname) {
      this.setData({
        tempNickname: nickname
      });
    }
  },

  // 昵称输入确认（按回车）
  onNicknameConfirm(e) {
    const nickname = e.detail.value;
    console.log('昵称输入确认，值:', nickname);
    if (nickname) {
      this.setData({
        tempNickname: nickname
      });
    }
  },

  // 确认用户信息
  async onConfirmUserInfo() {
    const { tempAvatarUrl, tempNickname, pendingUserData } = this.data;
    
    if (!tempAvatarUrl && !tempNickname) {
      wx.showToast({
        title: '请选择头像或填写昵称',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '保存中...', mask: true });

    try {
      let serverAvatarUrl = '';

      // 上传头像（如果有）
      if (tempAvatarUrl) {
        console.log('开始上传头像...');
        try {
          const uploadRes = await userApi.uploadAvatar(tempAvatarUrl);
          if (uploadRes && uploadRes.code === 0 && uploadRes.data && uploadRes.data.avatar_url) {
            serverAvatarUrl = uploadRes.data.avatar_url;
            console.log('头像上传成功:', serverAvatarUrl);
          }
        } catch (uploadErr) {
          console.error('头像上传失败:', uploadErr);
        }
      }

      // 更新昵称（如果有）
      if (tempNickname) {
        try {
          const updateRes = await userApi.updateWechatUserInfo(tempNickname, null);
          console.log('更新昵称响应:', updateRes);
        } catch (updateErr) {
          console.error('更新昵称失败:', updateErr);
        }
      }

      // 保存用户信息到本地
      wx.setStorageSync('userInfo', {
        id: pendingUserData?.id,
        openid: pendingUserData?.openid,
        nickName: tempNickname || '微信用户',
        avatarUrl: getFullAvatarUrl(serverAvatarUrl) || '',
        avatarText: '👤',
        level: '黄金会员',
        isWechatUser: true,
        createdAt: pendingUserData?.created_at
      });

      // 获取完整用户信息
      await this.fetchFullUserInfo();

      wx.hideLoading();
      this.setData({ 
        showUserInfoModal: false,
        pendingUserData: null
      });

      wx.showToast({
        title: '注册成功',
        icon: 'success',
        duration: 1000
      });

      this.navigateToIndex();

    } catch (err) {
      wx.hideLoading();
      console.error('保存用户信息失败', err);
      wx.showToast({
        title: '保存失败，请稍后重试',
        icon: 'none'
      });
    }
  },

  // 跳过用户信息设置
  onSkipUserInfo() {
    const { pendingUserData } = this.data;
    
    // 使用默认信息保存
    wx.setStorageSync('userInfo', {
      id: pendingUserData?.id,
      openid: pendingUserData?.openid,
      nickName: '微信用户',
      avatarUrl: '',
      avatarText: '👤',
      level: '黄金会员',
      isWechatUser: true,
      createdAt: pendingUserData?.created_at
    });

    this.setData({ 
      showUserInfoModal: false,
      pendingUserData: null
    });

    wx.showToast({
      title: '注册成功',
      icon: 'success',
      duration: 1000
    });

    this.navigateToIndex();
  },

  // 跳转到首页
  navigateToIndex() {
    console.log('navigateToIndex被调用');
    setTimeout(() => {
      wx.reLaunch({
        url: '/pages/index/index',
        success: () => {
          console.log('reLaunch成功');
        },
        fail: (err) => {
          console.error('reLaunch失败:', err);
          wx.switchTab({
            url: '/pages/index/index',
            fail: (err2) => {
              console.error('switchTab也失败:', err2);
              wx.redirectTo({
                url: '/pages/index/index',
                fail: (err3) => {
                  console.error('redirectTo也失败:', err3);
                }
              });
            }
          });
        }
      });
    }, 1000);
  },

  // 查看用户协议
  onViewAgreement() {
    wx.navigateTo({
      url: '/pages/agreement/agreement?type=user'
    });
  },

  // 查看隐私政策
  onViewPrivacy() {
    wx.navigateTo({
      url: '/pages/agreement/agreement?type=privacy'
    });
  }
});
