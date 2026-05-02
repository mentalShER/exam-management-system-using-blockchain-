from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from .encryption import *
from .a_encryption import *
from django.conf import settings
from django.core.files import File
import os, requests
import hashlib, json, base64

try:
	from web3 import Web3, EthereumTesterProvider
	w3 = Web3(EthereumTesterProvider())
except Exception:
	w3 = None

# Create your views here.
def user_login(request):
	if request.user.role == 'teacher':
		return redirect('teacher_dashboard')
	if request.user.role == "coe":
		return redirect('coe_dashboard')
	if request.user.role == 'superintendent':
		return redirect('st_dashboard')

@login_required(login_url='login')
@csrf_exempt
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url='login')
@csrf_exempt
def teacher_dashboard(request):
	p_request = Request.objects.filter(tusername=request.user.username,status='Pending')
	a_request = Request.objects.filter(tusername=request.user.username).exclude(status='Pending')
	if request.method == 'POST':
		if request.POST.get('accept'):
			username = request.user.username
			b_id = request.POST['b_id']
			Request.objects.filter(tusername=username,id=b_id).update(status='Accepted')
			messages.success(request, 'Request Accepted! Click on Accepted Request Section on check your requests.',extra_tags='accept')
		else:
			paper = request.FILES.get('paper',None)
			key = encrypt_file(paper)
			
			enc_path = os.path.join(settings.ENCRYPTION_ROOT, str(paper)+'.encrypted')
			with open(enc_path, 'rb') as f:
				hash_id = "Qm" + hashlib.sha256(f.read()).hexdigest()
			
			arr = a_encryption(hash_id,key,request.user.teacher_id)
			enc_json = json.dumps([base64.b64encode(x).decode('utf-8') for x in arr])
			
			b_id = request.POST.get('b_id')
			file_ = open(os.path.join(settings.ENCRYPTION_ROOT,request.user.teacher_id+'_private_key.pem'),'rb')
			p_file = File(file_)
			store = Request.objects.get(tusername=request.user.username, id=b_id)
			store.private_key.save(request.user.teacher_id+'_private_key.pem',p_file,save=True)
			store.enc_field = enc_json
			store.status = 'Uploaded'
			store.save()
			
			# Save mapping of hash to file for coe_dashboard to retrieve
			with open(os.path.join(settings.ENCRYPTION_ROOT, hash_id + '.mapping'), 'w') as mf:
				mf.write(str(paper)+'.encrypted')
				
			if w3:
				tx_hash = w3.eth.send_transaction({
					'from': w3.eth.accounts[0],
					'to': w3.eth.accounts[1],
					'data': w3.to_hex(text=hash_id)
				})
				messages.success(request, f'Paper uploaded! Blockchain Tx Hash: {w3.to_hex(tx_hash)}', extra_tags='upload')
			else:
				messages.success(request, 'Paper uploaded successfully!', extra_tags='upload')
	return render(request,'teacher.html',{'p_request':p_request,'a_request':a_request})

class DummyResponse:
	def __init__(self, text):
		self.text = text

@login_required(login_url='login')
@csrf_exempt
def coe_dashboard(request):
	if request.method == "POST":
		s_code = request.POST.get('s_code')
		t_id = request.POST.get('t_id')
		
		if not t_id:
			messages.error(request, 'Please select a paper before finalizing.')
			return redirect('coe_dashboard')
			
		Request.objects.filter(s_code=s_code).exclude(id=t_id).delete()
		queryset,created = Request.objects.update_or_create(id=t_id,defaults={'status':'Finalized'})
		messages.success(request, 'Paper has been finalized and sent to respective superintendent.')
		f_papers = Request.objects.filter(id=t_id).values('tusername','enc_field','private_key','s_code')
		for paper in f_papers:
			teacher = CustomUser.objects.filter(username=paper['tusername']).values('course','semester','branch','subject')
			try:
				enc_list = [base64.b64decode(x) for x in json.loads(paper['enc_field'])]
			except Exception:
				enc_list = paper['enc_field']
				
			values = a_decryption([enc_list,paper['private_key']])
			hash_id = values[1].decode('utf-8')
			
			# Retrieve from local mock instead of IPFS
			map_path = os.path.join(settings.ENCRYPTION_ROOT, hash_id + '.mapping')
			with open(map_path, 'r') as mf:
				enc_filename = mf.read().strip()
				
			enc_path = os.path.join(settings.ENCRYPTION_ROOT, enc_filename)
			with open(enc_path, 'r', encoding='utf-8', errors='ignore') as f:
				dummy_r = DummyResponse(f.read())
				
			final_paper = decrypt_file(dummy_r,values[0],paper['s_code'])
			FinalPapers.objects.create(s_code=paper['s_code'],course=teacher[0]['course'],semester=teacher[0]['semester'],
				branch=teacher[0]['branch'],subject=teacher[0]['subject'])
			final = FinalPapers.objects.latest('id')
			final.paper.save(paper['s_code']+'.pdf',final_paper,save=True)
	requests_ = Request.objects.values('tusername','status')
	arr = []
	for r in requests_:
		name = CustomUser.objects.filter(username=r['tusername']).values('first_name','last_name')
		arr.append({'name':name[0]['first_name']+ " " + name[0]['last_name'],'status':r['status']})
	return render(request,'coe.html',{'arr':arr})

@login_required(login_url='login')
@csrf_exempt
def st_dashboard(request):
	queryset = FinalPapers.objects.all()
	return render(request,'superintendent.html',{'queryset':queryset})

def get_teachers(request):
	course = request.POST.get('course',None)
	semester = request.POST.get('semester',None)
	branch = request.POST.get('branch',None)
	subject = request.POST.get('subject',None)
	s_code = SubjectCode.objects.filter(subject=subject).values()
	queryset1 = Request.objects.filter(s_code=s_code[0]['s_code']).values('tusername').distinct()
	queryset2 = Request.objects.filter(s_code=s_code[0]['s_code'],status='Uploaded').values('id')
	queryset = CustomUser.objects.filter(course=course,semester=semester,branch=branch,subject=subject).exclude(username__in=queryset1).values()
	data = { 'queryset':list(queryset),'s_code':s_code[0]['s_code'],'queryset2':list(queryset2) }
	return JsonResponse(data)

def add_teacher(request):
	s_code = request.POST.get('s_code',None)
	syllabus = request.FILES.get('syllabus',None)
	q_pattern = request.FILES.get('q_pattern',None)
	t_id = request.POST.get('g_id')
	deadline = request.POST.get('deadline',None)
	username = CustomUser.objects.filter(id=t_id).values('username')
	Request.objects.create(tusername=username[0]['username'],s_code=s_code,syllabus=syllabus,q_pattern=q_pattern,deadline=deadline)
	new_teacher = CustomUser.objects.filter(username=username[0]['username']).values()
	return JsonResponse({'new_teacher':list(new_teacher)})