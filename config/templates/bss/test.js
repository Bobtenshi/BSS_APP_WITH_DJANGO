async function func_start() {
  await func(2000, true);
  await func(3000, true);
  await func(1000, true);
}

function func(param_1, param_2) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      if (param_2) {
        console.log(`success:${param_1}`);
        resolve('成功');
      } else {
        reject('失敗');
      }
    }, param_1);
  });
}

let n_itr = 100
async function douki() {
  for (let itr = 1; itr <= n_itr; itr++) {
    //await ShowProgressBar(progress_pk, itr)
    //await cycle_bss(progress_pk, bss_method, itr, n_itr)
    //await res(itr, n_itr)
    await func(500, true);
    await console.log(a);
  }
}

//func_start();
douki();