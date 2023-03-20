class Action{
    constructor(parameter) {
        this._form = $('.form');
        this._email =  this._form.find('input[name=email]');
        this._phone =  this._form.find('input[name=phone]');
        this._reg_email = /^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/;
        this._reg_phone = /^1\w{10}$/;
        this._add_event();
    }
    _add_event(){
        let that = this;
        this._form.submit(function(){
            let email = that._email.val();
            let phone = that._phone.val();
            if(!that._reg_email.test(email)){
                alert('邮箱格式错误！');
                return false;
            }else if(!that._reg_phone.test(phone)){
                alert('手机号格式错误！');
                return false;
            }
        });
    }
}